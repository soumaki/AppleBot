#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

. init/logbot/logbot.sh
. init/utils.sh
. init/checks.sh

trap handleSigTerm TERM
trap handleSigInt INT
trap 'echo hi' USR1

initUserge() {
    printLogo
    assertPrerequisites
    sendMessage "Iniciando o AppleBot"
    assertEnvironment
    editLastMessage "Iniciando..."
    printLine
}

startUserge() {
    startLogBotPolling
    runPythonModule userge "$@"
}

stopUserge() {
    sendMessage "Encerrando o AppleBot ..."
    endLogBotPolling
}

handleSigTerm() {
    log "Encerrando com SIGTERM (143) ..."
    stopUserge
    exit 143
}

handleSigInt() {
    log "Encerrando com SIGINT (130) ..."
    stopUserge
    exit 130
}

runUserge() {
    initUserge
    startUserge "$@"
    local code=$?
    stopUserge
    return $code
}
