from turboactivate import (
    TurboActivate,
    #IsGenuineResult,
    TurboActivateError,
    TurboActivateTrialExpiredError,
    TA_USER,
    TA_SYSTEM
)

# Don't use 0 for either of these values.
# We recommend 90, 14. But if you want to lower the values
#  we don't recommend going below 7 days for each value.
# Anything lower and you're just punishing legit users.
DAYS_BETWEEN_CHECKS = 90
GRACE_PERIOD_LENGTH = 14

if __name__ == "__main__":

    # support both Python 2 and 3
    # for this simple example app
    try:
        input = "raw_input"
    except NameError:
        pass

    # now begins the licensing bit of the code
    isGenuine = False

    try:
        # TODO: go to the version page at LimeLM and
        # paste this GUID here
        ta = TurboActivate("e2w5q6vbvtkm4tgdesasnyyob76wbgy", TA_USER)

        # Check if we're activated, and every 90 days verify it with the activation servers
        # In this example we won't show an error if the activation was done offline
        # (see the 3rd parameter of the IsGenuine() function)
        # https://wyday.com/limelm/help/offline-activation/
        gen_r = ta.is_genuine_ex(DAYS_BETWEEN_CHECKS, GRACE_PERIOD_LENGTH, True)

        isGenuine = (gen_r == IsGenuineResult.Genuine
                     or gen_r == IsGenuineResult.GenuineFeaturesChanged

                     # an internet error means the user is activated but
                     # TurboActivate failed to contact the LimeLM servers
                     or gen_r == IsGenuineResult.InternetError
                     )

        if not isGenuine and ta.is_activated():

            # There is still activation data on the computer, and it's valid.

            # This means that IsGenuineEx() is saying "not activated" (a.k.a. TA_FAIL)
            # because the customer blocked connections to the activation servers (intentionally or not)
            # for nDaysBetweenChecks + nGraceDaysOnInetErr days.

            # What you should do now is prompt the user telling them before they can use your app that they need
            # to reverify with the activation servers.

            print('You must reverify with the activation servers before you can use this app. ')
            print('Type R and then press enter to retry after you\'ve ensured that you\'re connected to the internet. ')
            print('Or to exit the app press X. ')

            while True:
                user_resp = sys.stdin.read(1)

                if user_resp == 'x' or user_resp == 'X':
                    sys.exit("Exiting now. Bye.")

                if user_resp == 'r' or user_resp == 'R':
                    # Now we're using TA_IsGenuine() to retry immediately. Note that we're not using
                    # TA_IsGenuineEx() because TA_IsGenuineEx() waits 5 hours after an internet failure
                    # before retrying to contact the servers. TA_IsGenuine() retries immediately.
                    igr = ta.is_genuine()

                    if igr == IsGenuineResult.Genuine or igr == IsGenuineResult.GenuineFeaturesChanged:
                        print('Successfully reverified with the servers! You can now continue to use the app!')
                        break
                    else:
                        print('Failed to reverify with the servers. ')
                        print('Make sure you\'re connected to the internet and that you\'re not blocking access to the activation servers. ')
                        print('Then press R to retry again. ')
                else:
                    print('Invalid input. Press R to try to reverify with the servers. Press X to exit the app.')

    except TurboActivateError as e:
        #sys.exit("Failed to check if activated: " + str(e))
        print("Failed to check if activated: " + str(e))