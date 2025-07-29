import os
import shutil

def main(args):
    if not os.path.isfile('config.yml'):
        print("config.yml not detected. Make sure you're in the package root directory.")
        return
    
    shutil.rmtree('in')
    shutil.rmtree('out')
    os.mkdir('in')
    os.mkdir('out')
    
if __name__ == "__main__":
    main('')