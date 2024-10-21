from dotenv import load_dotenv
import os

# ----------------------------------------------------------------------------------------------------------------------
#
# MAIN - To be used for tests only!
#
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    # Load the .env file
    load_dotenv()

    password = os.getenv("PASS")
    phone_number = os.getenv("NUMBER")

    stand_alone = False

    if stand_alone:

        from ho_mobile_account.ho_mobile import HoMobile

        ho_mobile = HoMobile(password)

        ho_mobile.get_phone_number_credit(phone_number)

    else:

        from custom_components.ho_mobile.ho_mobile import HoMobile

        ho_mobile = HoMobile(params={
            'phone_number': phone_number,
            'password': password
        })
        import asyncio
        asyncio.run(ho_mobile.fetch_data())
        import time
        time.sleep(5)
        asyncio.run(ho_mobile.fetch_data())





