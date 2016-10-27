import sys
sys.path.append("..")
import model.code_model as code_model
import secret.config as config
import base64

def main():
    if len(sys.argv) != 3:
        print "python generate_code.py <path> <type>"
    else:
        data = {"path": sys.argv[1], "type": sys.argv[2]}
        data_transfer = code_model.encrypt_code(data, config.AES_KEY, config.AES_IV)
        print data_transfer

if __name__ == "__main__":
    main()
