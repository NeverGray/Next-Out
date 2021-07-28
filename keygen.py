import json
import sys
import threading

import requests

KEYGN_ACCOUNT_ID = "11635372-552d-48aa-aa1b-8b927fcaccd2"


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

        print(f'[keygen.validate_license_key_with_fingerprint] license_id={license_id} machine_fingerprint={machine_fingerprint} errors={to_error_message(errs)}',
              file=sys.stderr)

        return None, license_id

    validation_code = validation['meta']['constant']

    print(
        f'[keygen.validate_license_key_with_fingerprint] validation_code={validation_code} license_id={license_id} machine_fingerprint={machine_fingerprint}')

    return validation_code, license_id, validation


def activate_machine_for_license(license_id, machine_fingerprint, floating_token):
    """
    Activates a machine for a license. Returns the activated machine's ID.
    """

    activation = requests.post(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines",
        headers={
            'Authorization': f"Bearer {floating_token}",
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        },
        data=json.dumps({
            'data': {
                'type': 'machines',
                'attributes': {
                    'fingerprint': machine_fingerprint
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

    print(
        f'[keygen.activate_machine_for_license] license_id={license_id} machine_id={machine_id} machine_fingerprint={machine_fingerprint}')

    return machine_id


def deactivate_machine(machine_id, activation_token):
    """
    Deactivates a machine. Returns a boolean indicating success or failure.
    """

    deactivation = requests.delete(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines/{machine_id}",
        headers={
            'Authorization': f"Bearer {activation_token}",
            'Accept': 'application/vnd.api+json'
        }
    )

    if deactivation.status_code != 204:
        data = deactivation.json()
        errs = data['errors']

        print(f'[keygen.deactivate_machine] machine_id={machine_id} errors={to_error_message(errs)}',
              file=sys.stderr)

        return False

    print(f'[keygen.deactivate_machine] machine_id={machine_id}')

    return True


def deactivate_machine_on_exit(machine_id, activation_token):
    """
    Deactivates a machine on exit signal. Exits program with exit code indicating deactivation success or failure.
    """

    # Previously used machine_fingerprint
    ok = deactivate_machine(machine_id, activation_token)
    if ok:
        sys.exit(0)
    else:
        sys.exit("License did not deactivate.")


def ping_heartbeat_for_machine(machine_id, keygen_activation_token):
    """
    Performs a hearbeat ping for a machine. Returns a boolean indicating success or failure.
    """

    ping = requests.post(
        f"https://api.keygen.sh/v1/accounts/{KEYGN_ACCOUNT_ID}/machines/{machine_id}/actions/ping-heartbeat",
        headers={
            'Authorization': f"Bearer {keygen_activation_token}",
            'Accept': 'application/vnd.api+json'
        }
    ).json()

    if 'errors' in ping:
        errs = ping['errors']

        print(f'[keygen.ping_heartbeat_for_machine] machine_id={machine_id} errors={to_error_message(errs)}',
              file=sys.stderr)

        return False

    print(f'[keygen.ping_heartbeat_for_machine] machine_id={machine_id}')

    return True


def maintain_hearbeat_for_machine(machine_id, keygen_activation_token):
    """
    Performs minutely hearbeat pings for a machine on a loop.
    """
    timer = threading.Timer(59.0, lambda: maintain_hearbeat_for_machine(
        machine_id, keygen_activation_token))
    # The thread is killed when all other (non Daemon) process end
    timer.setDaemon(True)
    ok = ping_heartbeat_for_machine(machine_id, keygen_activation_token)
    if not ok:
        sys.exit("Heart beat failed to ping.")

    timer.start()
