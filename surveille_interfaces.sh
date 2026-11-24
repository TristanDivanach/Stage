#!/usr/bin/env bash
# surveille_interfaces.sh — Surveillance de l'état des interfaces d'un switch via SNMP (IF-MIB)
#
# Usage :
#   ./surveille_interfaces.sh [-H hôte] [-c community] [-i intervalle] [-l fichier_log] [-u] [-w]
#
#   -H  IP du switch              (défaut : 172.1.250.253)
#   -c  community SNMP v2c        (défaut : binome1)
#   -i  intervalle en secondes    (défaut : 10, mode -w uniquement)
#   -l  fichier de log            (défaut : ./interfaces.log)
#   -u  n'afficher que les interfaces administrativement actives (no shutdown)
#   -w  mode surveillance : boucle infinie, signale chaque changement d'état
#
# Exemples :
#   ./surveille_interfaces.sh                 # affiche l'état une fois
#   ./surveille_interfaces.sh -u              # seulement les ports activés
#   ./surveille_interfaces.sh -w -i 5         # surveille toutes les 5 s

HOST="172.1.250.253"
COMMUNITY="binome1"
INTERVAL=10
LOGFILE="./interfaces.log"
ONLY_ENABLED=0
WATCH=0

while getopts "H:c:i:l:uwh" opt; do
    case $opt in
        H) HOST=$OPTARG ;;
        c) COMMUNITY=$OPTARG ;;
        i) INTERVAL=$OPTARG ;;
        l) LOGFILE=$OPTARG ;;
        u) ONLY_ENABLED=1 ;;
        w) WATCH=1 ;;
        *) sed -n '2,19p' "$0"; exit 0 ;;
    esac
done

# OID IF-MIB (numériques -> pas besoin des MIB)
OID_DESCR="1.3.6.1.2.1.2.2.1.2"       # ifDescr
OID_ADMIN="1.3.6.1.2.1.2.2.1.7"       # ifAdminStatus  1=up 2=down 3=testing
OID_OPER="1.3.6.1.2.1.2.2.1.8"        # ifOperStatus   1=up 2=down ...
OID_ALIAS="1.3.6.1.2.1.31.1.1.1.18"   # ifAlias (description configurée)

# Couleurs (désactivées si la sortie n'est pas un terminal)
if [ -t 1 ]; then
    VERT=$'\e[32m'; ROUGE=$'\e[31m'; GRIS=$'\e[90m'; JAUNE=$'\e[33m'; RAZ=$'\e[0m'
else
    VERT=""; ROUGE=""; GRIS=""; JAUNE=""; RAZ=""
fi

command -v snmpwalk >/dev/null || { echo "snmpwalk introuvable (apt install snmp)"; exit 1; }

declare -A DESCR ADMIN OPER ALIAS PREV

# snmpwalk -> lignes "index valeur"
walk() {
    snmpwalk -v2c -c "$COMMUNITY" -t 2 -r 1 -m "" -Onqe "$HOST" "$1" 2>/dev/null \
        | sed -E "s/^\.?$1\.([0-9]+) /\1 /; s/\"//g"
}

etat_txt() {
    case $1 in
        1) echo up ;; 2) echo down ;; 3) echo testing ;; 5) echo dormant ;;
        6) echo notPresent ;; 7) echo lowerLayerDown ;; *) echo "unknown($1)" ;;
    esac
}

collecte() {
    DESCR=(); ADMIN=(); OPER=(); ALIAS=()
    local idx val
    while read -r idx val; do DESCR[$idx]=$val; done < <(walk "$OID_DESCR")
    [ ${#DESCR[@]} -eq 0 ] && return 1
    while read -r idx val; do ADMIN[$idx]=$val; done < <(walk "$OID_ADMIN")
    while read -r idx val; do OPER[$idx]=$val;  done < <(walk "$OID_OPER")
    while read -r idx val; do ALIAS[$idx]=$val; done < <(walk "$OID_ALIAS")
    return 0
}

# Indices triés numériquement
indices() { printf '%s\n' "${!DESCR[@]}" | sort -n; }

affiche() {
    local nb_up=0 nb_down=0 nb_off=0
    printf '\n%s — %s — %s\n' "$(date '+%F %T')" "$HOST" "$1"
    printf '%-6s %-24s %-8s %-15s %s\n' "Index" "Interface" "Admin" "Oper" "Description"
    printf '%.0s-' {1..72}; echo
    for i in $(indices); do
        local a=${ADMIN[$i]:-0} o=${OPER[$i]:-0}
        [ "$ONLY_ENABLED" -eq 1 ] && [ "$a" != 1 ] && { ((nb_off++)); continue; }
        local couleur
        if   [ "$a" != 1 ]; then couleur=$GRIS;  ((nb_off++))
        elif [ "$o" == 1 ]; then couleur=$VERT;  ((nb_up++))
        else                     couleur=$ROUGE; ((nb_down++))
        fi
        printf '%s%-6s %-24s %-8s %-15s %s%s\n' "$couleur" "$i" "${DESCR[$i]}" \
            "$(etat_txt "$a")" "$(etat_txt "$o")" "${ALIAS[$i]}" "$RAZ"
    done
    echo "Total : ${VERT}${nb_up} up${RAZ}, ${ROUGE}${nb_down} down${RAZ} (activées mais sans lien), ${GRIS}${nb_off} shutdown${RAZ}"
}

log() {
    local ligne="$(date '+%F %T') $HOST $*"
    echo "$ligne"
    echo "$ligne" | sed -E 's/\x1b\[[0-9;]*m//g' >> "$LOGFILE"
}

# --- Programme principal ---
if ! collecte; then
    echo "${ROUGE}Pas de réponse SNMP de $HOST (community '$COMMUNITY').${RAZ}"
    exit 2
fi
NOM=$(snmpget -v2c -c "$COMMUNITY" -m "" -Oqv "$HOST" 1.3.6.1.2.1.1.5.0 2>/dev/null | tr -d '"')
affiche "${NOM:-?}"

[ "$WATCH" -eq 0 ] && exit 0

for i in "${!DESCR[@]}"; do PREV[$i]="${ADMIN[$i]}/${OPER[$i]}"; done
log "Début de la surveillance (intervalle ${INTERVAL}s)"
JOIGNABLE=1
trap 'log "Fin de la surveillance"; exit 0' INT TERM

while sleep "$INTERVAL"; do
    if ! collecte; then
        [ $JOIGNABLE -eq 1 ] && log "${ROUGE}ALERTE : switch injoignable en SNMP${RAZ}"
        JOIGNABLE=0
        continue
    fi
    [ $JOIGNABLE -eq 0 ] && log "${VERT}Switch de nouveau joignable${RAZ}"
    JOIGNABLE=1

    for i in $(indices); do
        actuel="${ADMIN[$i]}/${OPER[$i]}"
        ancien="${PREV[$i]:-}"
        if [ -z "$ancien" ]; then
            log "${JAUNE}Nouvelle interface : ${DESCR[$i]}${RAZ}"
        elif [ "$actuel" != "$ancien" ]; then
            o=${OPER[$i]}
            [ "$o" == 1 ] && c=$VERT || c=$ROUGE
            log "${c}${DESCR[$i]} : admin $(etat_txt "${ancien%/*}") -> $(etat_txt "${ADMIN[$i]}"), oper $(etat_txt "${ancien#*/}") -> $(etat_txt "$o")${RAZ}"
        fi
        PREV[$i]=$actuel
    done
done
