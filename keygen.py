import base64
import json
import os
import sys
import threading

import ed25519
import requests

print_message = False
#Turn off logging from requests over the internet.
#from cryptography.exceptions import InvalidSignature
#from cryptography.hazmat.backends import default_backend
#from cryptography.hazmat.primitives import hashes, serialization
#from cryptography.hazmat.primitives.asymmetric import padding

KEYGN_ACCOUNT_ID = "11635372-552d-48aa-aa1b-8b927fcaccd2"

KEYGEN_PUBLIC_KEY = '52bd96f2e1649060125967aa9a6e177c59ab665c0fde1ebf723b646ef3cb073c'

def to_error_message(errs):
    """
    Formats an array of error dicts into an error message string. Returns an error message.
    """

    return ', '.join(map(lambda e: f"{e['title']}: {e['detail']}", errs))


def validate_license_key_with_fingerprint(license_key, machine_fingerprint):
    """
    Validates a license key scoped to a machine fingerprint. Returns a validation code and the license's ID.
    """

    validation = requests.post(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/licenses/actions/validate-key",
        headers={
            # 'Authorization': f"License {license_key}",
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        },
        data=json.dumps({
            'meta': {
                'scope': {'fingerprint': machine_fingerprint},
                'key': license_key
            }
        })
    ).json()

    license_id = None
    if 'data' in validation:
        data = validation['data']
        if data != None:
            license_id = data['id']

    if 'errors' in validation:
        errs = validation['errors']

        if print_message:
            print(f'[keygen.validate_license_key_with_fingerprint] license_id={license_id} machine_fingerprint={machine_fingerprint} errors={to_error_message(errs)}',
                file=sys.stderr)

        return None, license_id

    validation_code = validation['meta']['constant']
    if print_message:
        print(
            f'[keygen.validate_license_key_with_fingerprint] validation_code={validation_code} license_id={license_id} machine_fingerprint={machine_fingerprint}')

    return validation_code, license_id, validation


def activate_machine_for_license(license_id, machine_fingerprint, keygen_key,user_email=None):
    """
    Activates a machine for a license. Returns the activated machine's ID.
    """
    #Use the default activation if user_email is empty
    if user_email is None:
        activation = requests.post(
            f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines",
            headers={
                'Authorization': f"License {keygen_key}",
                'Content-Type': 'application/vnd.api+json',
                'Accept': 'application/vnd.api+json'
            },
            data=json.dumps({
                'data': {
                    'type': 'machines',
                    'attributes': {
                        'fingerprint': machine_fingerprint,
                    },
                    'relationships': {
                        'license': {
                            'data': {'type': 'licenses', 'id': license_id}
                        }
                    }
                }
            })
        ).json()
    #Track the "user_email" in Keygen to help organization track authorized computers
    else:
        activation = requests.post(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines",
        headers={
            'Authorization': f"License {keygen_key}",
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        },
        data=json.dumps({
            'data': {
                'type': 'machines',
                'attributes': {
                    'fingerprint': machine_fingerprint,
                    'metadata':{
                        'userEmail': user_email
                    }
                },
                'relationships': {
                    'license': {
                        'data': {'type': 'licenses', 'id': license_id}
                    }
                }
            }
        })
        ).json()       

    if 'errors' in activation:
        errs = activation['errors']

        print(f'[keygen.activate_machine_for_license] license_id={license_id} machine_fingerprint={machine_fingerprint} errors={to_error_message(errs)}',
              file=sys.stderr)

        return None

    machine_id = activation['data']['id']

    if print_message:
        print(
            f'[keygen.activate_machine_for_license] license_id={license_id} machine_id={machine_id} machine_fingerprint={machine_fingerprint}')

    return machine_id


def deactivate_machine(machine_id, keygen_key):
    """
    Deactivates a machine. Returns a boolean indicating success or failure.
    """

    deactivation = requests.delete(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines/{machine_id}",
        headers={
            'Authorization': f"License {keygen_key}",
            'Accept': 'application/vnd.api+json'
        }
    )

    if deactivation.status_code != 204:
        data = deactivation.json()
        errs = data['errors']

        print(f'[keygen.deactivate_machine] machine_id={machine_id} errors={to_error_message(errs)}',
              file=sys.stderr)

        return False
    if print_message:
        print(f'[keygen.deactivate_machine] machine_id={machine_id}')

    return True


def deactivate_machine_on_exit(machine_id, keygen_key):
    """
    Deactivates a machine on exit signal. Exits program with exit code indicating deactivation success or failure.
    """

    # Previously used machine_fingerprint
    ok = deactivate_machine(machine_id, keygen_key)
    if ok:
        sys.exit(0)
    else:
        sys.exit("License did not deactivate.")


def ping_heartbeat_for_machine(machine_id, keygen_key):
    """
    Performs a hearbeat ping for a machine. Returns a boolean indicating success or failure.
    """

    ping = requests.post(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines/{machine_id}/actions/ping-heartbeat",
        headers={
            'Authorization': f"License {keygen_key}",
            'Accept': 'application/vnd.api+json'
        }
    ).json()

    if 'errors' in ping:
        errs = ping['errors']

        print(f'[keygen.ping_heartbeat_for_machine] machine_id={machine_id} errors={to_error_message(errs)}',
              file=sys.stderr)

        return False

    if print_message:
        print(f'[keygen.ping_heartbeat_for_machine] machine_id={machine_id}')

    return True


def maintain_hearbeat_for_machine(machine_id, keygen_key):
    """
    Performs minutely hearbeat pings for a machine on a loop.
    """
    timer = threading.Timer(59.0, lambda: maintain_hearbeat_for_machine(
        machine_id, keygen_key))
    # The thread is killed when all other (non Daemon) process end
    timer.setDaemon(True)
    ok = ping_heartbeat_for_machine(machine_id, keygen_key)
    if not ok:
        sys.exit("Heart beat failed to ping.")

    timer.start()

def verify_ed25519(sig, msg):
  # Load the hex-encoded verify key from the env
  verify_key = ed25519.VerifyingKey(
    KEYGEN_PUBLIC_KEY.encode(),
    encoding='hex'
  )

  # Verify the license
  try:
    verify_key.verify(sig, msg)

    return True
  except ed25519.BadSignatureErr:
    return False

def verify_offline_license_key(license_key):

    # Split license key to obtain key and signature, then decode base64url encoded values
    signing_data, enc_sig = license_key.split(".")
    prefix, enc_key       = signing_data.split("/")
    assert prefix == 'key', 'license key prefix %s is invalid' % prefix

    sig = base64.urlsafe_b64decode(enc_sig)
    key = base64.urlsafe_b64decode(enc_key)

    ok = verify_ed25519(sig, ("key/%s" % enc_key).encode())

    key_info = json.loads(key.decode("utf-8"))

    return ok, key_info
