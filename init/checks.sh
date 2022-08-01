#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

_checkBashReq() {
    log "Verificando os comandos em Bash ..."
    command -v jq &> /dev/null || quit "Comando solicitado : jq : não encontrado !"
}

_checkPythonVersion() {
    log "Conferindo a versão do Python ..."
    getPythonVersion
    ( test -z $pVer || test $(sed 's/\.//g' <<< $pVer) -lt 3${minPVer}0 ) \
        && quit "Obrigatório pelo menos a versão 3.$minPVer.0 do Python!"
    log "\tPYTHON encontrado - v$pVer ..."
}

_checkConfigFile() {
    log "Conferindo dados do arquivo de configurações ..."
    configPath="config.env"
    if test -f $configPath; then
        log "\tArquivo encontrado : $configPath, Exportando ..."
        set -a
        . $configPath
        set +a
        test ${_____REMOVA_____ESTA_____LINHA_____:-fasle} = true \
            && quit "Please remove the line mentioned in the first hashtag from the config.env file"
    fi
}

_checkRequiredVars() {
    log "Conferindo ENV Vars obrigatórias ..."
    for var in API_ID API_HASH LOG_CHANNEL_ID DATABASE_URL; do
        test -z ${!var} && quit "Obrigatório a var $var!"
    done
    [[ -z $HU_STRING_SESSION && -z $BOT_TOKEN ]] && quit "Obrigatório a HU_STRING_SESSION ou a var do BOT_TOKEN!"
    [[ -n $BOT_TOKEN && -z $OWNER_ID ]] && quit "Obrigatório a var do OWNER_ID!"
    test -z $BOT_TOKEN && log "\t[HINT] >>> BOT_TOKEN não encontrado! (Desativando logs avançados)"
}

_checkDefaultVars() {
    replyLastMessage "Conferindo ENV Vars padrões ..."
    declare -rA def_vals=(
        [WORKERS]=0
        [PREFERRED_LANGUAGE]="en"
        [DOWN_PATH]="downloads"
        [UPSTREAM_REMOTE]="upstream"
        [UPSTREAM_REPO]="https://github.com/applled/AppleBot"
        [LOAD_UNOFFICIAL_PLUGINS]=true
        [CUSTOM_PLUGINS_REPO]=""
        [G_DRIVE_IS_TD]=true
        [CMD_TRIGGER]="."
        [SUDO_TRIGGER]="!"
        [FINISHED_PROGRESS_STR]="🍏"
        [UNFINISHED_PROGRESS_STR]="🍊"
        [NEKO_API]="https://hmtai.herokuapp.com/nsfw/"
    )
    for key in ${!def_vals[@]}; do
        set -a
        test -z ${!key} && eval $key=${def_vals[$key]}
        set +a
    done
    if test $WORKERS -le 0; then
        WORKERS=$(($(nproc)+4))
    elif test $WORKERS -gt 32; then
        WORKERS=32
    fi
    export MOTOR_MAX_WORKERS=$WORKERS
    export HEROKU_ENV=$(test $DYNO && echo 1 || echo 0)
    DOWN_PATH=${DOWN_PATH%/}/
    if [[ $HEROKU_ENV == 1 && -n $HEROKU_API_KEY && -n $HEROKU_APP_NAME ]]; then
        local herokuErr=$(runPythonCode '
import heroku3
try:
    if "'$HEROKU_APP_NAME'" not in heroku3.from_key("'$HEROKU_API_KEY'").apps():
        raise Exception("Invalid HEROKU_APP_NAME \"'$HEROKU_APP_NAME'\"")
except Exception as e:
    print(e)')
        [[ $herokuErr ]] && quit "heroku response > $herokuErr"
    fi
    for var in G_DRIVE_IS_TD LOAD_UNOFFICIAL_PLUGINS; do
        eval $var=$(tr "[:upper:]" "[:lower:]" <<< ${!var})
    done
    local uNameAndPass=$(grep -oP "(?<=\/\/)(.+)(?=\@cluster)" <<< $DATABASE_URL)
    local parsedUNameAndPass=$(runPythonCode '
from urllib.parse import quote_plus
print(quote_plus("'$uNameAndPass'"))')
    DATABASE_URL=$(sed 's/$uNameAndPass/$parsedUNameAndPass/' <<< $DATABASE_URL)
}

_checkDatabase() {
    editLastMessage "Checando a DATABASE_URL ..."
    local mongoErr=$(runPythonCode '
import pymongo
try:
    pymongo.MongoClient("'$DATABASE_URL'").list_database_names()
except Exception as e:
    print(e)')
    [[ $mongoErr ]] && quit "Conectando-se - pymongo > $mongoErr" || log "\tpymongo solicitado > {status : 200}"
}

_checkTriggers() {
    editLastMessage "Analisando os TRIGGERS ..."
    test $CMD_TRIGGER = $SUDO_TRIGGER \
        && quit "Inválido SUDO_TRIGGER! Você não pode usar $CMD_TRIGGER como SUDO_TRIGGER"
}

_checkPaths() {
    editLastMessage "Analisando os Paths ..."
    for path in $DOWN_PATH logs; do
        test ! -d $path && {
            log "\tCriando Path : ${path%/} ..."
            mkdir -p $path
        }
    done
}

_checkUpstreamRepo() {
    remoteIsExist $UPSTREAM_REMOTE || addUpstream
    editLastMessage "Buscando por informações no UPSTREAM_REPO ..."
    fetchUpstream || updateUpstream && fetchUpstream || quit "Variável para UPSTREAM_REPO é inválida!"
    fetchBranches
    updateBuffer
}

_setupPlugins() {
    local link path tmp
    if test $(grep -P '^'$2'$' <<< $3); then
        editLastMessage "Clonando $1 Plugins ..."
        link=$(test $4 && echo $4 || echo $3)
        tmp=Temp-Plugins
        gitClone --depth=1 $link $tmp
        replyLastMessage "\tInstalando Requisitos ..."
        upgradePip
        installReq $tmp
        path=$(tr "[:upper:]" "[:lower:]" <<< $1)
        rm -rf userge/plugins/$path/
        mv $tmp/plugins/ userge/plugins/$path/
        cp -r $tmp/resources/. resources/
        rm -rf $tmp/
        deleteLastMessage
    else
        editLastMessage "$1 Plugins Desabilitados!"
    fi
}

_checkUnoffPlugins() {
    _setupPlugins Xtra true $LOAD_UNOFFICIAL_PLUGINS https://github.com/applled/extras.git
}

_checkCustomPlugins() {
    _setupPlugins Custom "https://([0-9a-f]{40}@)?github.com/.+/.+" $CUSTOM_PLUGINS_REPO
}

_flushMessages() {
    deleteLastMessage
}

assertPrerequisites() {
    _checkBashReq
    _checkPythonVersion
    _checkConfigFile
    _checkRequiredVars
}

assertEnvironment() {
    _checkDefaultVars
    _checkDatabase
    _checkTriggers
    _checkPaths
    _checkUpstreamRepo
    _checkUnoffPlugins
    _checkCustomPlugins
    _flushMessages
}
