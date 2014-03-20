#!/bin/bash

SESSION_NAME="SIDs"

tmux has-session -t ${SESSION_NAME}
status=$?
if [ $status != 0 ] ; then
    # create session
    tmux new-session -d -s ${SESSION_NAME} -n Server

    # First pane
    tmux send-keys -t ${SESSION_NAME} 'python main.py' C-m

    # Second pane
    tmux split-window -h -t ${SESSION_NAME}
    tmux send-keys -t ${SETSSION_NAME}:0.1 'livereload .' C-m
fi

tmux attach-session -t ${SESSION_NAME}
