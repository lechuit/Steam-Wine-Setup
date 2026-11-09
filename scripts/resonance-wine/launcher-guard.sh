# BEGIN RESONANCE process detection
# Rosetta may expose the Windows image path as the macOS process name.
resonance_game_pid() {
  ps -axo pid=,comm= 2>/dev/null | awk -v root="$STEAM_COMPAT_INSTALL_PATH" '
    BEGIN { root = tolower(root); sub(/\/$/, "", root) }
    {
      pid = $1
      name = $0
      sub(/^[[:space:]]*[0-9]+[[:space:]]+/, "", name)
      gsub(/\\/, "/", name)
      name = tolower(name)
      sub(/^z:/, "", name)
      if (root == "" || index(name, root "/") != 1) next
      if (name ~ /\/ffrs-win64-shipping\.exe$/) main_pid = pid
      if (name ~ /\/ffrs\.exe$/) bootstrap_pid = pid
    }
    END { if (main_pid != "") print main_pid; else if (bootstrap_pid != "") print bootstrap_pid }
  '
}
# END RESONANCE process detection
