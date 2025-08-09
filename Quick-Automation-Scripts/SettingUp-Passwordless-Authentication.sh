#! /bin/bash

file=Path_to_your_hosts/Servers             # Replace this with you path to file
key=Path_to_Your_Public_key                 # Replace this with your path to Key

While IFS= read -r host; do
[[ -z "$host" || "$host" =~ *\s*\[.*\] ]] && continue
#The above line will skip empty line or Grouping, Normally that we do while managind Nodes

ssh-copy-id -f "-o IdentityFile=$key" "$host"

done < "$file"
  
