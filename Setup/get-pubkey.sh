file="$HOME/.ssh/id_rsa.pub"
if [ ! -f "$file" ]; then
    yes "" | ssh-keygen
fi
echo
echo "This is your pubkey: "
cat "$file"