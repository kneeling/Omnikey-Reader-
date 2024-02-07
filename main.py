from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException
from smartcard.util import toHexString
from pyasn1.codec.der import decoder
from pyasn1_modules import rfc2459
from colorama import init, Fore

init(autoreset=True)

def format_date(date_bytes):
    return "Formatted Date"

def process_card_data(data):

    formatted_data = """
    Application
        AID: ...
        Label: ...
        ...
        ... (other fields)
    """
    return formatted_data

def main():
    cardtype = AnyCardType()
    cardrequest = CardRequest(timeout=1000, cardType=cardtype)
    cardservice = cardrequest.waitforcard()

    if cardservice is None:
        print(f"{Fore.LIGHTRED_EX}No card detected.")
        return

    print(f"{Fore.LIGHTGREEN_EX}Card detected.{Fore.RESET}")

    try:
        cardservice.connection.connect()
        aid = bytearray.fromhex("A0000000031010")  # VISA AID
        select_apdu = [0x00, 0xA4, 0x04, 0x00, len(aid)] + list(aid) + [0x00]
        response, sw1, sw2 = cardservice.connection.transmit(select_apdu)

        if sw1 == 0x61:
            get_response_apdu = [0x00, 0xC0, 0x00, 0x00, sw2]
            response, sw1, sw2 = cardservice.connection.transmit(get_response_apdu)

        if sw1 == 0x90 and sw2 == 0x00:
            print("Response in SELECT:", toHexString(response))

            # Check if visa or mastercard
            if aid == bytearray.fromhex("A0000000031010"):
                if aid == bytearray.fromhex("A0000000031010"): #if visa \ i did it twice because im  too lazy to reindent everything
                    print(f"CARD TYPE : {Fore.LIGHTBLUE_EX}VISA {Fore.LIGHTYELLOW_EX}DEBIT{Fore.RESET}")
                    for rec in range(1, 6):  # Assuming records 1 to 5 contain data
                        read_apdu = [0x00, 0xB2, rec, 0x04, 0x00]
                        response, sw1, sw2 = cardservice.connection.transmit(read_apdu)
                        if sw1 == 0x61:
                            get_response_apdu = [0x00, 0xC0, 0x00, 0x00, sw2]
                            response, sw1, sw2 = cardservice.connection.transmit(get_response_apdu)
                        if sw1 == 0x90 and sw2 == 0x00:
                            print("Record #" + str(rec))
                            formatted_data = process_card_data(response)
                            print(formatted_data)
                        else:
                            print("Record #" + str(rec), "Error:", hex(sw1), hex(sw2))
                    return #to exit and close everything
            elif aid == bytearray.fromhex("A0000000041010"):
                print(f"CARD TYPE : {Fore.LIGHTRED_EX}MASTER{Fore.LIGHTYELLOW_EX}CARD{Fore.RESET}")

            for sfi in range(1, 32):
                for rec in range(1, 17):
                    read_apdu = [0x00, 0xB2, rec, ((sfi << 3) | 4), 0x00]
                    response, sw1, sw2 = cardservice.connection.transmit(read_apdu)
                    if sw1 == 0x61:
                        get_response_apdu = [0x00, 0xC0, 0x00, 0x00, sw2]
                        response, sw1, sw2 = cardservice.connection.transmit(get_response_apdu)
                    if sw1 == 0x90 and sw2 == 0x00:
                        print("SFI", hex(sfi), "record #" + str(rec))
                        formatted_data = process_card_data(response)
                        print(formatted_data)
                    else:
                        print("SFI", hex(sfi), "record #" + str(rec), "Error:", hex(sw1), hex(sw2))

        else:
            print("Error selecting AID:", hex(sw1), hex(sw2))
    except CardConnectionException as e:
        print(f"Card Connection Exception: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Waiting for card to be inputted")
    main()
