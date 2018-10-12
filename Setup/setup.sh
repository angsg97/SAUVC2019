read -p "Press [enter] to continue"

# Download the Miniconda install script and verify it

wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-`uname -m`.sh
md5sum Miniconda3-latest-Linux-`uname -m`.sh

# Install Miniconda! Then delete the install file

bash Miniconda3-latest-Linux-`uname -m`.sh
rm Miniconda3-latest-Linux-`uname -m`.sh

source ~/.bashrc
export PATH="$HOME/miniconda3/bin:$PATH"

# setup conda in bashrc
declare -a file_appends=(
	'. $HOME/miniconda3/etc/profile.d/conda.sh'
)

target_file="$HOME/.bashrc"

for i in "${file_appends[@]}" ; do
  if ! grep -Fxq "$i" "$target_file" ; then
	echo "$i" >> "$target_file"
  else
	:
  fi
done

# create conda environment
echo -e "\nCreating SAUVC Conda Environment..."
conda create -n SAUVC python=3.6

# Activate the SAUVC conda environment
echo -e "\nActivating conda SAUVC environment..." 
source activate SAUVC

# Install dependencies
echo -e "\nInstalling dependencies..."
pip install imutils
conda install scipy cython
conda install -c conda-forge opencv
pip install pyserial

# run test code
echo
echo "Running test code, press q to exit"
python test.py

# Done
exec bash
