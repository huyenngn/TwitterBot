from twitter import *

def main():
    ta = Client()
    ta.delete_all_rules()
    ta.set_rules()
    ta.get_stream()


if __name__ == "__main__":
    main()