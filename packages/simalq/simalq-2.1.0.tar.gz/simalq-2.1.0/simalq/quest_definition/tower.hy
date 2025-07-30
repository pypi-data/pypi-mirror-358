;; * Front matter

(import
  fractions [Fraction :as f/]
  toolz [partition]
  simalq.game-state [Rules]
  simalq.quest-definition [mk-quest])
(setv  T True  F False)

(setv name "Wizard's Tower")

(defn quest-fn []

(defn m [#* args]
  {
    "▒▒" "Void"
    "++" "door"
    "<1" ["wallfall trap" :wallnum 1]
    "█1" ["trapped wall" :wallnum 1]
    "$2" "handful of gems"
    "% " "snack"
    "%%" "meal"
    #** (dict (partition 2 args))})

(setv quest (mk-quest

  :name name
  :authors "Kodi B. Arfer"
  :title "A stack of cozy 15-by-15 levels. It's time to climb."

  :player-starting-hp 150
  :reality-bubble-size Inf
  :dainty-monsters F

  #* (.values {

;; * Level definitions

;  :map "
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . ."

1 [:title "It's clobberin' time"
  :poison-intensity (f/ 1 5)
  :map "
    $2. . . ██. ########M ####██. 
    . . . . ██. ############d2██. 
    . . . . ██. ##██####d2####ld>
    M . . . ██. ##############██. 
    . . . . ██. ##Z ##########██. 
    ████ld████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    . . . . ██. . . $ $ $ d . ++. 
    . M TP. ██. TP. $ $ $ d . ██{2
    . . . . ██. . @ $ $ $ d . ██.
    ////////██. . . $ $ $ d k ██M
    . . . . ██. . . $ $ $ . . ██.
    . . . . ████++██████████████.
    . . . . ██. . . . . . . . . .
    . 0e. . ██. . . . . . . . . .
    . . . . ██{1. . . . . . . . ."
  :map-marks (m
    "d2" ["devil" :hp 2]
    "{1" ["gate" :target "{2"]
    "{2" ["gate" :target "{1"]
    "##" ["cracked wall" :hp 1]
    "//" "web"
    "K " ["Dark Knight" :hp 5]
    "ld" "locked door"
    "k " "key"
    "TP" "teleporter"
    "0e" "earthquake bomb"
    "M " ["golem" :hp 3])]

2 [:title "What's that smell?"
  :poison-intensity (f/ 10)
  :map "
    A . . { . . { . % { . . { . .
    . . . . . . . . . . . . . . .
    . . . . . . . . . . G . . . @
    . { . G . { . . G . . . . . .
    . . . . . . . . . . . . . . {
    . . . . . . . . . . . . G . .
    ++{ . . . { . . . G . . . . .
    <p███1█1█1█1. . . . . . . { .
    <a███1█1█1█1. . . . ☉G. . . .
    . { █1█1█1{ . . . . . . . . .
    . ███1█1█1█1. . . . . . { . .
    . ███1█1█1█1. { <1. . . . . .
    . { █1█1█1{ . . . . . . . . .
    ☉d██0p█1☉d█1. . . . . . . { .
    > ███1█1█1█1. . . . { . . ☉o."
  :map-marks (m
    "{ " "water fountain"
    "G " ["ghost" :hp 2]
    "A " ["Death" :hp 2]
    "☉G" ["generator" :hp 2
      :summon-frequency (f/ 1 3)
      :summon-class "ghost"
      :summon-hp 2]
    "☉o" ["generator" :hp 2
      :summon-frequency (f/ 1 6)
      :summon-class "orc"
      :summon-hp 3]
    "☉d" ["generator" :hp 3
      :summon-frequency (f/ 1 9)
      :summon-class "devil"
      :summon-hp 3]
    "<p" "paralysis trap"
    "<a" "arrow trap"
    "0p" "poison-gas bomb")]

3 [:title "Defend yourself"
  :poison-intensity (f/ 1 10)
  :map "
    . . . . . . % > % . . . . . .
    . . . . . . . . . . . . . . .
    K K K K K K K K K K K K K K K
    █1█1█1█1█1█1█1█1█1█1█1█1█1█1█1
    . . . . . . . . . . . . . . .
    . . . . . . . <1. . . . . . .
    . . . . . . . . . . . . . . .
    . . . . . . . . . . . . . . .
    . . . . . . . . . . . . . . .
    . . . ■ ■ ■ ■ ■ ■ ■ ■ ■ . . .
    . . . . . . . . . . . . . . .
    . . . ■ ■ ■ ■ ■ ■ ■ ■ ■ . . .
    . . . . . . . . . . . . . . .
    . . . . . . . . . . . . . . .
    @ . . . . . . . . . . . . . ."
  :map-marks (m
    "K " ["Dark Knight" :hp 3]
    "■ " "pushblock")]

4 [:title "Spiderbro"
  :poison-intensity (f/ 1 5)
  :map "
    . . . . . / . @ . . . . . ld>
    . . . . . . . . . . . . . ldld
    . . . . f . . . . . . . . . .
    . . . . . . . . . . f . . . .
    f . . . . . f . . . . . . . .
    . . S#. . . . S#. . . . S#. .
    . . . . . . . . . . . . . . f
    . . . . . . . . . . f . . . .
    . . . f . . . f . . . . . . .
    . . S#. . . . S#. . . . S#. .
    f . . Z . . . . . . . Z . . .
    . . S#. . f . S#. . . . S#. .
    . . . . . . . . . . . . . . .
    . . . . . . , , , . . . . . f
    %%f . . . f , k , . . Z . . ."
  :map-marks (m
    ", " "pile of debris"
    "ld" "locked door"
    "/ " "wand of flame"
    "k " "key"
    "S#" #(["giant spider" :hp 4] "web"))]



; - Maybe a version of "Defend yourself" with specters

;? [:title "You decide"
;  :poison-intensity XKodi
;  :map "
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . ▒▒+↓▒▒. . . . . .
;    . . . . . ▒▒▒▒( ▒▒▒▒. . . . .
;    . . . . . +→[ > / +←. . . . .
;    . . . . . ▒▒▒▒) ▒▒▒▒. . . . .
;    . . . . . . ▒▒+↑▒▒. . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . .
;    . . . . . . . . . . . . . . ."
;  :map-marks (m
;    "/ " "wand of death")]

;; * End matter

})))

quest)
