# SAUVC2019
Repositoryfor SUTD SAUVC 2019 team

## Guide
### Useful Git Tips

To make things easier, I will add all software team members' public key to deploy keys so that we can push code directly to this repository

To get your ssh public key, run Setup/get-pubKey.sh , then you should get a key start with "ssh-rsa"

After your key is added to project deploy keys, you should be able to clone this project using ssh (if you used https to clone this project before, please delete it and do it with ssh. This will allow you to push code)

    git clone git@github.com:heyuhang0/SAUVC2019.git

To get lastest update, simplely run

    git pull

To publish your changes, please proceed in the following order

    # 1. get latest update
    git pull

    # 2. check conflict, test code (never push without testing)

    # 3. check what you are going to upload, using
    git status  # show all changed files
    git diff    # show all changed lines

    # 3. commit your changes
    git commit -a -m "(Explain what you did?)" # this will upload all changes in files, or
    # if you want to add new files or only want to upload specific changes
    # git add file1, file2 ...(files that you want to upload)
    # git commit -m "(Explain what you did?)"

    # 4. push changes to server
    git push

### Environment

To set up environment, run Setup/setup.sh scipt using (please use deafult setting when installing): 

    bash setup.sh

This should install miniconda and create a virtual environment named SAUVC with all dependencies needed

Then you should be able to run test code using:

    # open a new terminal
    # cd into /Setup folder
    conda activate SAUVC # activate virtual environment
    python test.py

The code should be able to indicate the green ball in the test picture
