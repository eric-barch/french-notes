from models.session import Session


def main():
    session = Session()

    session.user_interface.choose_deck()
    session.user_interface.request_input()


if __name__ == "__main__":
    main()
