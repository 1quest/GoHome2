export FLASK_APP=home.py
handler(){
    read
    [ "$REPLY" = "clean" ] || kill -INT -$$
}

# invoke handler as a coprocess.
coproc handler
xdg-open http://127.0.0.1:5000/
flask run
echo clean >&"${COPROC[1]}"
