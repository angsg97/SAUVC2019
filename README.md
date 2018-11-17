# SAUVC2019
Repositoryfor SUTD SAUVC 2019 team

## Guide
### Get ssh-key

Get into Setup file and give executive authority to the file get-pubkey.sh and run it. REMENBER to keep the ssh key you get ! 

~~~
chmod +x get-pubkey.sh
./get-pubkey.sh
~~~

After getting the ssh key, go to Github click on the right top ==> settings  ==>  SSH and GPG keys, 

Click New SSH key to get the ssh key and paste the SSH. 

After adding the SSH key to your own account contact the author to add collaborators.

When you get the invitation link press accept, Congratulations! you are participate in this project.

### Useful Git Tips

After you accept the invite linnk and become a collaborator, you should be able to clone this project using ssh (if you used https to clone this project before, please delete it and do it with ssh. This will allow you to push code)

    git clone git@github.com:heyuhang0/SAUVC2019.git

To get lastest update, simplely run:

    git pull

To publish your changes, please proceed in the following order

    # 1. check what you are going to upload, using
    git status  # show all changed files
    git diff    # show all changed lines
    
    # 2. commit your changes
    git commit -a -m "(Explain what you did?)" # this will upload all changes in files, or
    # if you want to add new files or only want to upload specific changes
    # git add file1, file2 ...(files that you want to upload)
    # git commit -m "(Explain what you did?)"
    
    # 3. get latest update
    git pull
    
    # 4. check conflict, test code (never push without testing)
    
    # 5. push changes to server
    git push

### Environment

To set up environment, run Setup/setup.sh scipt using (please use deafult setting when installing): 

    bash setup.sh

This should install miniconda and create a virtual environment named SAUVC with all dependencies needed.

Then you should be able to run test code using:

    # open a new terminal
    # cd into /Setup folder
    conda activate SAUVC # activate virtual environment
    python test.py

The code should be able to indicate the green ball in the test picture

If you have ros kinetic installed which may conflict with openCV, you may need to delete openCV installed by ros using:

    rm /opt/ros/kinetic/lib/python2.7/dist-packages/cv2.so
