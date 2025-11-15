# TODO: Implement Search and Play Features for Google and YouTube

## Tasks
- [ ] Add searchGoogle function to engine/features.py
- [ ] Add PlayYoutube function to engine/features.py
- [ ] Update allCommands in engine/command.py to handle "search on google" and "play on youtube/google" commands
- [ ] Test the new voice commands

## Details
- searchGoogle: Extract query after "search" and "on google", open Google search URL.
- PlayYoutube: Extract query after "play" and "on youtube", open YouTube search URL.
- For "play on google": Treat as search on Google (since Google doesn't play videos directly).
- Update allCommands with new elif conditions.
