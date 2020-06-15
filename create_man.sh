#!/bin/bash
#This script was autogenerated with the --create-script option of cli2man

function man_disco() {
    cli2man -i man/disco_help.txt --see-also disco_mix,disco-suggest,disco-import,disco-search --os DiscoDOS --include man/disco_add.mdoc $1
}
function man_disco_mix() {
    cli2man -i man/disco_mix_help.txt --os DiscoDOS --info-section "arguments" --set-order "NAME,SYNOPSIS,DESCRIPTION,ARGUMENTS,OPTIONS,AUTHORS,SEE ALSO" --see-also disco,disco-suggest,disco-import,disco-search,discosync --include man/disco_mix_add.mdoc $1

}
function man_disco_suggest() {
    cli2man -i man/disco_suggest_help.txt --os DiscoDOS --info-section "arguments" --set-order "NAME,SYNOPSIS,DESCRIPTION,ARGUMENTS,OPTIONS,AUTHORS,SEE ALSO" --include man/disco_suggest_add.mdoc --see-also disco,disco-mix,disco-import,disco-search,discosync $1
}
function man_disco_import() {
    cli2man -i man/disco_import_help.txt --see-also disco,disco-mix,disco-suggest,disco-search --os DiscoDOS --include man/disco_sub_add.mdoc $1
}
function man_disco_search() {
    cli2man -i man/disco_search_help.txt --see-also disco,disco-mix,disco-suggest,disco-import --os DiscoDOS --include man/disco_sub_add.mdoc $1
}
function man_discosync() {
    cli2man -i man/discosync_help.txt --see-also disco,disco-mix,disco-suggest,disco-import,disco-search --os DiscoDOS --include man/discosync_add.mdoc $1
}

if [ "$1" == 'doit' ]; then
    #man_disco > man/disco.mdoc
    man_disco_mix > man/disco-mix.mdoc
    #man_disco_suggest > man/disco-suggest.mdoc
    #man_disco_import > man/disco-import.mdoc
    #man_disco_search > man/disco-search.mdoc
    #man_discosync > man/discosync.mdoc
    echo "5 files written to man/"
    echo "Now fix stuff manually"
else
    #man_disco -m
    man_disco_mix -m
    #man_disco_suggest -m
    #man_disco_import -m
    #man_disco_search -m
    #man_discosync -m
fi

