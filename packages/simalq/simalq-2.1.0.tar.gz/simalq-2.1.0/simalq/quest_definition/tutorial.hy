;; * Front matter

(import
  fractions [Fraction :as f/]
  simalq.quest-definition [mk-quest])
(setv  T True  F False)

(setv name "Tutorial Quest")

(defn quest-fn []

(defn t [x]
  (.replace x "\\n" "\n"))

(setv quest (mk-quest
  :name name
  :authors "Kodi B. Arfer"
  :title #[[An instructive introduction to Infinitesimal Quest 2 + ε, inspired by Yves Meynard's "Boot Camp 2".]]
  :player-starting-hp 500

  #* (.values {

;; * Level definitions

1 [:title (t #[[You are Princess Triskaidecagonn XIII, represented by the symbol "@". Your goal in each quest is to escape the dungeon alive, with as many points as possible. Points are awarded for killing monsters and collecting items.\n\nHit "?" (Shift-/) for the controls. Use look mode to learn what each thing on the screen is and what it does.]])
  :map "
    . . . . . ██. $ $ . ██. . | ██. . .
    . . . . . ██. . . . ██. | . ██. ██.
    . . @ . . . . . . . ██. ██. ██. ██.
    . . . . . ██. . . . ██. ██. ██. ██.
    . . . . . ██. $2$2. . . ██. . . ██.
    ████████████████████████. ████████.
    . . . . . | . | . | . | . . . . . .
    . . . . . . | . | . | . . . . . . .
    > . . . . | . | . | . | . . . . . .
    . . . . . . | . | . | . . . . . . .
    . . . . . | . | . | . | . . . . . ."
  :map-marks {
    "$2" "handful of gems"}]

2 [:title (t #[[Tris's mastery of diviniation magic allows her to predict the future. In game terms, this means that the game is fully deterministic, and you can undo as many actions as you like. You can even undo back to a previous level. In the status bar, next to the turn counter, a negative number shows how many actions you've undone, and hence how many you can redo.\n\nYou can also freely save the game and load your saves. One command overwrites your main save slot. Another one makes a "checkpoint" save that's never overwritten. Each saved game maintains an independent undo history.]])
  :map "
     . . . . . . . @ . . . . . . . .
     . . . . . . . . . . . . . . . .
     . . . . . . . . . . . . . . . .
     +↓██+↓██+↓██+↓████+↓██+↓██+↓██+↓
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██$
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██$ ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██$ ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██$ ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     . ██. ██. ██. ████. ██. ██. ██.
     $ ██. ██. ██. ████. ██. ██. ██.
     ██████████████████████████+↓████
     . . . . . . . . > . . . . . . ."]

3 [:title "Many dungeon levels are filled with poisonous air. Sadly, the monsters have gotten used to it, so it only hurts you. The status bar shows how much poison you're breathing in each turn. Once you have 1 or more units of this poison in your system, it's converted to damage, which is deducted from your hit points (HP).\n\nYou can probably guess what happens when you run out of HP (but this, too, can be undone). Pick up food to regain HP.\n\nLevels can wrap around."
  :poison-intensity (f/ 1 5)
  :wrap-x T
  :map "
    ██| . | . . . . . . . .
    ██. @ . . . . . %s. . .
    ██| . | . . . . . . . .
    ████████████████████. .
    . . . %s. . . . . ██. .
    . . . . . . . . . ██. .
    ████████████████. ██████
    . . . %m. . > ██. . . . "
  :map-marks {
    "%s" "snack"
    "%m" "meal"}]

4 [:title (t #[[The dungeons are full of unpleasant characters who are better off dead. You can attack them with your sword (by bumping into them) or your bow (with a command). You have infinite arrows, but they do only 1 damage apiece, whereas your sword does 2 damage.\n\nMonsters can only do anything when they're in the "reality bubble" centered on you. Likewise, your arrows can't travel outside the reality bubble.]])
  :poison-intensity (f/ 1 10)
  :map "
    . . . . . ██. . . . . . . . . . . . .
    . . @ . . ██> . . . . . . . . . . . .
    . . . . . ██. . . . . . . . . . . . .
    ##########██. . . . . . . w . . w . .
    ████████##██. . . . . . . . . . . . .
    . . . ██##██. . . . . . . . . . . . .
    . . . ██++██████████. . . . . . . . .
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██████████████████++
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . | . | . . K2
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . . . . . . .
    . . . . . . . . . ██. . . | . | . . K2
    . . . . K3. . . . ██. . . . . . . . .
    ████████████████. ++. . . . . . . . ."
  :map-marks {
    "##" ["cracked wall" :hp 1]
    "++" "door"
    "K3" ["Dark Knight" :hp 3]
    "K2" ["Dark Knight" :hp 2]}]

5 [:title "Monsters are color-coded according to their current HP. Use look mode to see the exact number.\n\nSome monsters do different amounts of damage based on their HP. In this case, in the monster's info screen, the different amounts of damage are separated by slashes, like 1 / 2 / [3], with the currently applicable amount indicated by brackets.\n\nGenerators pump out monsters endlessly, but you can destroy them. Position the reality bubble carefully and use your bow to minimize the number of monsters they produce before you blow them apart."
  :poison-intensity (f/ 1 10)
  :map "
    . . . . . . . . . . . . ++o3
    . . . . . . . . . . . . ██o2
    . . . . . . . . . . . . ██o1
    . . ☉o. . . . . . . . . ██X
    . . . . . . . . . . . . ██.
    > . . . . . . . . . . . ██x
    . . . . . . . . . . . . ██.
    . . . . . . . . . . . . ██.
    . . . . . . . . . . . . ██.
    ██████████████████████████.
    ████████████. . @ . . . . .
    ████████████████████████████
    ████████████w1w2w3w4w5w6w7w8"
  :map-marks {
    "++" "door"
    "x " ["wallfall trap" :wallnum 1]
    "X " ["trapped wall" :wallnum 1]
    "☉o" ["generator" :hp 3
      :summon-class "orc"
      :summon-frequency (f/ 1 2)
      :summon-hp 1]
    #** (dfor
      i (range 10)
      mon ["orc" "wizard"]
      f"{(get mon 0)}{i}" [mon :hp i])}]

6 [:title "Monsters aren't very bright. Take advantage of their simplemindedness to even the odds.\n\nCan you complete this level without taking damage? Don't forget that you can undo moves that you regret."
  :map "
  ▒▒▒▒▒▒. . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  ▒▒. . . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  . . . . . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
  . @ . . . . . . . . ++. . . . . . . . d . . . . . . . . . . . >
  . . . . . . . . o . ++. . . . . . . . . . . . . . ██████K ▒▒▒▒▒▒
  . . . . . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. ██. ██. ▒▒▒▒▒▒
  ▒▒. . . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. ██. ██. ▒▒▒▒▒▒
  ▒▒▒▒▒▒. . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. ██. . . ▒▒▒▒▒▒"
  :map-marks {
    "▒▒" "Void"
    "++" "door"
    "o " ["orc" :hp 3]
    "d " ["devil" :hp 2]
    "K " ["Dark Knight" :hp 8]}]

7 [:title "All sorts of useful items can be found lying around. Some have an immediate effect, while others sit in your inventory until you decide to use them."
  :poison-intensity (f/ 1 10)
  :map "
    ██ld. . ! . . . ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ██ld██. . . . {}▒▒▒▒. . . . o o o ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ██ld████████████▒▒▒▒. . . . o $ o ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . k k k k k ▒▒▒▒. . . . o o o ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . k k k k k ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . k k k k k ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . . . . . . ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ██ld████████████▒▒▒▒++████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . . . . . . ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . @ . . k . . . ▒▒▒▒. . . . . . . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . . . . . . ▒▒▒▒. 0101020203. ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. /w/w/s/s. . ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . . ◀▶w ◀▶. . .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ld. . . . ◀▶██◀▶. . .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . . . <1██. . .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . . . . ██◀▶◀▶.
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . | . . ◀▶w ◀▶.
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . . . . ◀▶◀▶◀▶.
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. d . d d d . ██. . . . . ◀▶◀▶◀▶. .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. d . ☉d. d . ██. . ■ | . ◀▶w ◀▶. .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. d . . . d . ██. . . . . ◀▶◀▶◀▶. .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. | | | . d . ██. . . . . . . . █1MS
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . ☉d. . | | ██. . . . . . . . . █1
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . ☉d██. . . . . . . . . .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒. . . . . . . ██. . . . . . . . . .
    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒> . . . . . . ██. . . . . . . . . ."
  :map-marks {
    "▒▒" "Void"
    "++" "door"
    "ld" "locked door"
    "■ " "pushblock"
    "<1" ["wallfall trap" :wallnum 1]
    "█1" ["trapped wall" :wallnum 1]
    "{}" ["gate" :target "$ "]
    "w " ["wizard" :hp 3]
    "☉d" ["generator" :hp 3
      :summon-class "devil"
      :summon-frequency (f/ 1 3)
      :summon-hp 1]
    "k " "key"
    "! " "amulet of invulnerability"
    "01" "standard bomb"
    "02" "strong bomb"
    "03" "super-bomb"
    "/w" "wall-making wand"
    "/s" "wand of shielding"
    "MS" "Magic Shield"}]

8 [:title "Your bow isn't just for shooting monsters. You can also shoot some other things for special effects."
  :poison-intensity (f/ 1 10)
  :map "
    . . @ . . ██. . . . . . . . . .
    . . . . . ██. . . . . . . . . .
    . . . ██████. . . . . . ◀▶. . .
    . . . ██. . . . . . . . ◀▶☉w. >
    ++██. ██++██. . . . . . 0 . . .
    o ██. ██o ██. . . . . . . . . .
    o ██◀▶██o ██. . . . . . . . . .
    o o ☠ o o ██. . . . . . . . . .
    o o o o o ██. . . . . . . . . ."
  :map-marks {
    "++" "door"
    "☠ " "jar of poison"
    "o " ["orc" :hp 3]
    "0 " "strong bomb"
    "☉w" ["generator" :hp 2
      :summon-class "wizard"
      :summon-frequency (f/ 1)
      :summon-hp 3]}]

9 [:title "Some levels have a time limit. When you run out of time, you automatically change to the dungeon level indicated in the status bar."
  :time-limit 15
  :map "
     ▒▒▒▒▒▒▒▒▒▒⏲ ▒▒▒▒▒▒▒▒▒▒
     ▒▒▒▒▒▒▒▒. . . ▒▒▒▒▒▒▒▒
     ▒▒▒▒▒▒. . . . . ▒▒▒▒▒▒
     ▒▒▒▒. . . . . . . ▒▒▒▒
     ▒▒. . . . . . . . . ▒▒
     $ . . . . @ . . . . $
     ▒▒. . . . . . . . . ▒▒
     ▒▒▒▒. . . . . . . ▒▒▒▒
     ▒▒▒▒▒▒. . . . . ▒▒▒▒▒▒
     ▒▒▒▒▒▒▒▒. . . ▒▒▒▒▒▒▒▒
     ▒▒▒▒▒▒▒▒▒▒$ ▒▒▒▒▒▒▒▒▒▒"
  :map-marks {
    "▒▒" "Void"
    "$ " "pile of gold"}]

10 [:title "Monsters have a variety of immunities, behavior, and special abilities. Check their info screens for the deets."
  :poison-intensity (f/ 1 8)
  :map "
    @ ██. . ++. . . ██i . . ++b . . . . . . . . ██>
    . ██. . ▒▒. . . ██. . . ▒▒. . b . . b . b . ██%
    . ██G G ▒▒. . . ██. i . ▒▒. . b . . . . . . ██.
    . ██G G ▒▒. . . ██. . . ▒▒. . . . b3. . b . ██.
    D ██☠ G ▒▒. . . ██i . . ▒▒. . . . . . . . . ██.
    T ██◀▶G ▒▒. . . ██. . i ▒▒. . . . . . b . . ██.
    . ██◀▶<>▒▒. . . ██. . . ▒▒b . . . . . . b . ██.
    . ++. . ▒▒. . . ++i . . ▒▒b . . b b . . . b ++."
  :map-marks {
    "▒▒" "Void"
    "++" "door"
    "<>" "fixed damaging trap"
    "☠ " "jar of poison"
    "% " "dessert"
    "D " ["Death" :hp 2]
    "T " ["thorn tree" :hp 2]
    "i " ["imp" :hp 2]
    "b3" ["bat" :hp 3]}]

11 [:title "Pop quiz! Escape this level to complete the tutorial."
  :poison-intensity (f/ 1 8)
  :map "
    . . . . . ██. . . . . ██. . . . . . ◀▶. . . . ◀▶. . . . <8
    . . . . . d ██. o3. ██. . . . . . . ◀▶. . . . ◀▶. . . . .
    . . . . . . d ██. ██. . . . . . . . ◀▶. ◀▶. . ◀▶. . . . .
    . . . . . . . . <>. . . . . . . . . ◀▶% ◀▶. . ◀▶. . . . .
    % . . . . . d ██. ██. . . . . . . . ◀▶N ◀▶◀▶◀▶◀▶. . . . .
    <4. . . . d ██. o3. ██. . . . . . . ++N ++. . . . . . . .
    ████████████████████████████████████████████████ld██████++
    <2☉BT . . . . . . . T . . . . . B T . . T 0 | | . | | . .
    . . T . . . . B . . T . . . . B . . . . B | | . | | . . .
    . . T . . . . . . . . . . . . . . . . . | | $$| | . . . .
    . . T1. . . . . . B . . . . T . . . . | | $$| | . . . . .
    . . . . . . T . . . B . . . . . . . | | $$| | . . . . . .
    ████████████████████████████████++██| . | | . . . . . . .
    ██. . ██d2██☉G. . . . . . . . . ☉Gld. | | ☉G. . . . . . .
    ██N ████. ██. . . . . . . . . . . ██████████████████████++
    ██. . ██. ██. . . . . . . . . . . ██. . . . . . . . . . .
    ██. . ██. ██. . . . . . . . . . . ██. . | | d2. . . . . .
    ██. . ██. ██. . . . . . . . . . . | . . . . . . . . . . .
    <5█8. █7. █6. . . . . @ . . . . . . . . . . . $ $ d2. ☉d<6
    ██. . ██. ██. . . . . . . . . . . | . . . . . . . . . . .
    ██. . ██. ██. . . . . . . . . . . ██. . | | d2. . . . . .
    ██. . ██. ██. . . . . . . . . . . ██. . . . . . . . . . .
    ████. ██. ██. . . . . . . . . . . ████████████████◀▶██████
    ██. N ██d2██☉G. . . . . . . . . K ++. . . . . . ☉oo o o3<1
    ██████████████████████++████████++████████████████████████
    <3. . . . . . . . . ███1██. . . . . . . . ████████████████
    t . . . . . . . . O ███2██. . . . . . . . ████. . . . . .
    . . . . . . . . . . ███3██. ■ . . . . . . ████. . . . . .
    . . . . . . . . . . ███4██. . . . . . . . ████. . . . . .
    . . . . . . . . . . ███5██. . . . . . . . ████S . . . . .
    . . . . . . . . . ██$$$$$$██. . . . . . . ████. . . . . .
    . . . . . . . . . ██$$> $$██. . . . . . . ████. . . . . .
    . . . . . . . . . ██$$$$$$██. . . . . . . ████████████████
    . . . . . . . . . . ██████. . . . . . . . . . ██████████$$
    t . . . . . . t . . . . . . . . . . . . . . . . . . . . <7"

  :map-marks {
    "++" "door"
    "ld" "locked door"
    "■ " "pushblock"
    "<>" "paralysis trap"
    "$ " "pile of gold"
    "$$" "handful of gems"
    "k " "key"
    "0 " "standard bomb"
    "% " "snack"
    "T " ["thorn tree" :hp 3]
    "T1" ["thorn tree" :hp 1]
    "K " ["Dark Knight" :hp 2]
    "t " ["Tricorn" :hp 4]
    "o3" ["orc" :hp 3]
    "S " ["specter" :hp 3]
    "☉G" ["generator" :hp 3
      :summon-class "ghost"
      :summon-frequency (f/ 1 3)
      :summon-hp 3]
    "d2" ["devil" :hp 2]
    "☉d" ["generator" :hp 2
      :summon-class "devil"
      :summon-frequency (f/ 1 2)
      :summon-hp 1]
    "☉o" ["generator" :hp 3
      :summon-class "orc"
      :summon-frequency (f/ 1)
      :summon-hp 1]
    "☉B" ["generator" :hp 2
      :summon-class "giant bee"
      :summon-frequency (f/ 1 4)
      :summon-hp 1]
    "O " ["blob" :hp 8]
    #** (dfor
      i (range 10)
      [k v] (.items {
        f"<{i}" ["wallfall trap" :wallnum i]
        f"█{i}" ["trapped wall" :wallnum i]})
      k v)}]

;; * End matter

})))

quest)
