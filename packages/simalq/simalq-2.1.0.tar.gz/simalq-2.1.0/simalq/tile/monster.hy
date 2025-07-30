;; --------------------------------------------------------------
;; * Imports
;; --------------------------------------------------------------

(require
  hyrule [unless do-n list-n defmacro-kwargs case ecase pun block]
  simalq.macros [field-defaults pop-integer-part defmeth]
  simalq.tile [deftile])
(import
  re
  fractions [Fraction :as f/]
  enum [Enum]
  hyrule [thru xor]
  toolz [unique]
  simalq.util [DamageType StatusEffect next-in-cycle mixed-number]
  simalq.geometry [Direction at dist adjacent? adj-or-eq? dir-to turn-and-pos-seed ray burst]
  simalq.game-state [G]
  simalq.tile [Tile Actor Damageable]
  simalq.tile.scenery [Scenery walkability can-occupy?])
(setv  T True  F False)

(pun

;; --------------------------------------------------------------
;; * Declarations
;; --------------------------------------------------------------

((fn [] (for [dt DamageType]
  (setv (get (globals) dt.name) dt))))

(setv undead-immunities #(Poison DeathMagic))

;; --------------------------------------------------------------
;; * The parent class
;; --------------------------------------------------------------

(defclass Monster [Actor Damageable]
  "A non-player character, typically out to kill the player."

  (setv
    damage-melee None
      ; How much damage the monster does with its basic melee attack.
      ; This can be `None` (for no melee attack), one number, or a
      ; tuple of numbers, with element 0 giving damage when the
      ; monster is at 1 HP, element 1 at 2 HP, etc. (the last element
      ; being implicitly repeated as required).
    damage-shot None
      ; Likewise for shots.
    shot-range None
      ; If set to an integer, it limits the distance at which the
      ; monster can shoot.
    kamikaze F
      ; If true, the monster kills itself upon attacking.
    sees-invisible F
      ; If true, the monster is unaffected by the player being invisible.
    vampirizable F
      ; If true, a vampire can turn this monster into another vampire.
    flavor-for-generator "In defiance of thermodynamics, this device pumps out monsters endlessly.")
      ; Flavor text for generators of this monster type.

  (defn [classmethod] points-for-generator [cls]
    "How many points the monster's generator is worth."
    (* 4 cls.destruction-points))

  (defn [classmethod] read-tile-extras [cls mk-pos v1 v2]
    (dict :hp v2))

  (defmeth damage-by-hp [damage]
    "Get the element from a damage tuple or single damage value
    (typically assigned to `@damage-melee` or `@damage-shot`) that
    should be used given the monster's current HP."
    (if (isinstance damage tuple)
      (get damage (- (min @hp (len damage)) 1))
      damage))

  (defmeth player-invisible-to? [[mon-pos None]]
    (and
      (.player-has? StatusEffect.Ivis)
      (not (adj-or-eq? (or mon-pos @pos) G.player.pos))
        ; Invisibility has no effect on adjacent monsters. They can
        ; smell your fear.
      (not @sees-invisible)))

  (setv special-melee None)
    ; A method to do a special effect instead of damage for a melee attack.
  (setv special-shot None)
    ; Likewise for shots.

  (defmeth try-to-attack-player [[dry-run F] [shots-ignore-obstacles F] [pos None]]
    "Try to melee or shoot the player, if the monster can. Return true
    if it succeeded. If `dry-run` is true, the attack isn't actually
    made."

    (setv pos (or pos @pos))
    (setv d (dir-to pos G.player.pos))
    (setv attack None)

    (when (= pos G.player.pos)
      ; If we're on the player's square, we can't attack her.
      (return F))

    (when (@player-invisible-to?)
      (return F))

    ; Try a melee attack first.
    (when (and
        (or @damage-melee @special-melee)
        (adjacent? pos G.player.pos)
        (in (get (walkability pos d :monster? T) 1)
          ['bump 'walk]))
      (setv attack 'melee))

    ; Otherwise, try a ranged attack.
    (when (and (not attack) (or @damage-shot @special-shot))
      (for [target (ray :!pos :direction d :length
          (min (or @shot-range Inf) G.rules.reality-bubble-size))]
        (when (= target G.player.pos)
          (setv attack 'shot)
          (break))
        (when (any (gfor
            tile (at target)
            (or tile.superblock (and
              tile.blocks-monster-shots
              (not shots-ignore-obstacles)))))
          (break))))

    ; Execute the attack (if we have one).
    (when dry-run
      (return (bool attack)))
    (setv special (case attack
      'melee @special-melee
      'shot @special-shot))
    (setv damage (case attack
      'melee @damage-melee
      'shot @damage-shot))
    (cond
      (and special (special))
        ; Make a special attack. (The effect has already happened, so
        ; just play an animation.)
        (.animate-hit G.player
          :attacker @
          :label "  "
          :special? T)
      damage
        ; Make a regular attack.
        (.damage G.player
          :attacker @
          :amount (@damage-by-hp damage)
          :damage-type (if (= attack 'shot) MonsterShot MonsterMelee))
      True
        ; We don't actually have a usable attack. Bail out.
        (return F))
    (when @kamikaze
      (@rm-from-map))
    T)

  (defmeth info-bullets [#* extra]
    (defn damage-array [damage]
      (if (isinstance damage tuple)
        (.join " / " (gfor
          d damage
          (if (= d (@damage-by-hp damage))
            f"[{d}]"
            (str d))))
        damage))

    (.info-bullets (super)
      (when @damage-melee
        #("Melee damage" (damage-array @damage-melee)))
      (@dod "Melee special attack" 'special-melee Monster)
      (when @damage-shot
        #("Shot damage" (damage-array @damage-shot)))
      (when @shot-range
        #("Shot range" @shot-range))
      (@dod "Shot special attack" 'special-shot Monster)
      (when @kamikaze
        #("Kamikaze" "When the monster attacks, it dies. You get no points for this."))
      (when @sees-invisible
        #("Invisibility detection" "The monster is unaffected by you being invisible."))
      (when @vampirizable
        #("Vampirizable" "This monster can be turned by a vampire."))
      (@dod "Effect when damaged" 'hook-damaged Damageable)
      (@dod "Effect on death" 'hook-destruction Damageable)
      #* extra
      (@dod "Behavior" 'act))))

;; --------------------------------------------------------------
;; * Common behavior classes
;; --------------------------------------------------------------

(defclass Stationary [Monster]
  (defmeth act []
    "Stationary — The monster attacks if it can, but is otherwise immobile."
    (@try-to-attack-player)))

(defclass Approacher [Monster]

  (field-defaults
    approach-dir None)
  (setv mutable-fields #("approach_dir"))
  (defmeth info-bullets [#* extra]
    (.info-bullets (super)
      #("Approach direction" @approach-dir)
      #* extra))

  (defmeth approach [
      [implicit-attack T]
      [advance-approach-dir T]
      [reverse F]
      [jump F]
      [ethereal-to #()]]
    "Approach — If the monster can attack, it does. Otherwise, it tries to get closer to you in a straight line. If its path to you is blocked, it will try to adjust its direction according to its approach direction. If it can't move that way, it wastes its turn, and its approach direction advances to the next cardinal direction."
    ; Return true if we successfully moved or attacked; false otherwise.

    (when (and implicit-attack (@try-to-attack-player))
      (return T))
    (when (@player-invisible-to?)
      (return F))

    ; Try to get closer to the player.
    (setv d (dir-to @pos G.player.pos))
    (when (is d None)
      ; The player is in our square. Just give up.
      (return F))
    (if reverse
      (setv d d.opposite)
      (when (and (adjacent? @pos G.player.pos) (in d Direction.orths))
        ; We're already as close as we can get, without entering the
        ; player's square.
        (return F)))

    (setv target None)
    (defn ok-target []
      (nonlocal target)
      (if jump
        ; In jump mode, we move two squares, mostly ignoring tiles on
        ; the intermediate square, and ignoring all diagonal blocking.
        (and
          (setx intermediate (+ @pos d))
          (not (any (gfor
            tile (at intermediate)
            (and (isinstance tile Scenery) tile.superblock))))
          (setx target (+ intermediate d))
          (can-occupy? target :monster? T :!ethereal-to))
        (do
          (setv [target wly] (walkability @pos d :monster? T :!ethereal-to))
          (= wly 'walk))))

    (unless (ok-target)
      ; We can't go that way. Try a different direction.
      ; Use a non-random equivalent of IQ's `ApproachHero`.
      (setv approach-dir
        (next-in-cycle Direction.orths @approach-dir))
      (when advance-approach-dir
        (setv @approach-dir approach-dir))
      (setv d (tuple (gfor
        c ["x" "y"]
        (int (xor (getattr approach-dir c) (getattr d c))))))
      ; Per IQ, we make only one attempt to find a new direction.
      ; So if this fails, give up.
      (when (= d #(0 0))
        (return F))
      (setv d (get Direction.from-coords d))
      (unless (ok-target)
        (return F)))

    ; We're clear to move.
    (@move target)
    (return T))

  (setv act approach))

(defclass Wanderer [Monster]

  (field-defaults
    wander-state None)
  (setv mutable-fields #("wander_state"))
  (defmeth suffix-dict []
    (dict
      #** (.suffix-dict (super))
     :wd (@preview-dirs 5)))
  (defmeth info-bullets [#* extra]
    (.info-bullets (super)
      #("Next few wandering directions" (+ (@preview-dirs 20)
        (if @wander-state "" " (this monster is not yet seeded, so values will change if it first acts on a later turn)")))
      #* extra))

  (defmeth wander [[implicit-attack T] [ethereal-to #()] [bump-hook None]]
    "Wander — If the monster can attack, it does. Otherwise, it chooses a direction (or, with equal odds as any given direction, nothing) with a simplistic pseudorandom number generator. It walks in the chosen direction if it can and the target square is inside the reality bubble."

    (when (and implicit-attack (@try-to-attack-player))
      (return))

    (setv [d @wander-state] (@pseudorandom-dir @wander-state))
    (unless d
      (return))
    (setv [target wly] (walkability @pos d :monster? T :!ethereal-to))
    (unless target
      (return))
    (when (> (dist G.player.pos target) G.rules.reality-bubble-size)
      (return))
    (when (and (in wly ['bump 'walk]) bump-hook)
      (bump-hook target)
      (setv [target wly] (walkability @pos d :monster? T :!ethereal-to)))
    (unless (= wly 'walk)
      (return))
    (@move target))

  (setv act wander)

  (defmeth pseudorandom-dir [state]
    "Use a linear congruential generator. Each seed should have a
    decent period coprime to the number of options (9)—long enough
    to look randomish, but not long.
    https://en.wikipedia.org/w/index.php?title=Linear_congruential_generator&oldid=1140372972#c_%E2%89%A0_0
    Return the next value and the next state."

    (setv  m (** 8 3)  c 1  a (+ 2 1))
    (setv options (+ Direction.all #(None)))
    (when (is state None)
      ; Seed the RNG.
      (setv state (% (turn-and-pos-seed @pos) m)))
    #(
      (get options (% state (len options)))
      (% (+ (* a state) c) m)))

  (defmeth preview-dirs [n]
    (.join "" (do
      (setv state @wander-state)
      (list-n n
        (setv [d state] (@pseudorandom-dir state))
        (if (is d None)
          "•"
          (get d.arrows d)))))))

(defclass Summoner [Monster]

  (field-defaults
    summon-dir None
    summon-power (f/ 0))
      ; A per-turn accumulator of summoning frequency.
  (setv mutable-fields #("summon_dir" "summon_power"))
  (defmeth suffix-dict []
    (dict
      #** (.suffix-dict (super))
     :pw (mixed-number @summon-power)))
  (defmeth info-bullets [#* extra]
    (.info-bullets (super)
      #("Summoning power" (mixed-number @summon-power))
      #("Summoning direction" @summon-dir)
      #* extra))

  (defmeth summon [stem frequency hp]
    "Increment summon power. Then, try to generate one or more monsters
    in adjacent spaces. Return true if power was expended."

    (+= @summon-power frequency)
    (when (< @summon-power 1)
      (return F))
    (do-n (pop-integer-part @summon-power)
      ; Find an empty square to place the new monster.
      (do-n (len Direction.all)
        (setv @summon-dir (next-in-cycle Direction.all @summon-dir))
        (setv target (+ @pos @summon-dir))
        (unless target
          (continue))
        (when (= (at target) [])
          (break))
        (else
          ; We couldn't find anywhere to place this monster. Just
          ; end summoning, wasting the consumed summon power.
          (return)))
      ; We have a target. Place the monster.
      (@make target stem :!hp))
    T))

;; --------------------------------------------------------------
;; * Generated monsters
;; --------------------------------------------------------------

(defclass Generated [Monster]
  "A monster that can be produced by a generator in IQ."

  (setv
    score-for-damaging T))

(defmacro self-sc [#* rest]
  `(. Tile.types [self.summon-class] ~@rest))

(deftile :name "generator" :superc Summoner
  ; An immobile structure that creates monsters nearby.

  :field-defaults (dict
    :summon-class "orc"
      ; The stem of the monster type to generate.
    :summon-frequency (f/ 1 4)
    :summon-hp 1)
      ; How many hit points each monster will be summoned with.
  :suffix-dict (meth []
    (dict
      #** (.suffix-dict (super))
      :freq (mixed-number @summon-frequency)
      :sHP @summon-hp))
  :info-bullets (meth []
    (.info-bullets (super)
      #("Summoning frequency" (mixed-number @summon-frequency))
      #("Type of summoned monsters" @summon-class)
      #("Hit points of summoned monsters" @summon-hp)))

  :mapsym (property-meth []
    (+ "☉" (self-sc mapsym [0])))
  :destruction-points (property-meth []
    (self-sc (points-for-generator)))

  :score-for-damaging (property-meth []
    (self-sc score-for-damaging))
  :immune (property-meth []
    ; Generators inherit all the immunities of the monsters they
    ; generate, and they're always immune to poison.
    (setv x (self-sc immune))
    (+ x (if (in Poison x) #() #(Poison))))

  :full-name (property-meth []
    (.format "{}{} {}"
      (if (self-sc article) (+ (self-sc article) " ") "")
      (.replace (self-sc stem) " " "-")
      (Tile.full-name.fget @)))

  :act (meth []
    "Generate — The generator adds its summon frequency to its summon power. If the total is more than 1, the integer part is removed and a corresponding number of monsters are generated in adjacent empty squares. If there are no adjacent empty squares, the expended summon power is wasted. The square that the generator attempts to target rotates through the compass with each summon or failed attempt."
    (@summon @summon-class @summon-frequency @summon-hp))

  :flavor (property-meth []
    (self-sc flavor-for-generator)))

(defmacro-kwargs defgenerated [
    mapsym name
    superc
    iq-ix-mon iq-ix-gen
    points-mon points-gen
    flavor-mon flavor-gen
    #** kwargs]
  "Shorthand for defining both a generated monster and its generator."

  (unless (isinstance superc hy.models.List)
    (setv superc [superc]))

  `(do

    (deftile ~mapsym ~name [Generated ~@superc]
      :iq-ix-mapper ["hp"
        ~(dict (zip iq-ix-mon [1 2 3]))]
      :destruction-points ~points-mon
      :points-for-generator (classmethod (fn [cls] ~points-gen))
      :flavor ~flavor-mon
      :flavor-for-generator ~flavor-gen
      ~@(hy.I.toolz.concat (gfor
        [k v] (.items kwargs)
        [(hy.models.Keyword k) v])))

    ((fn [] (for [[iq-ix hp] (zip ~iq-ix-gen [1 2 3])]
      (setv (get Tile.types-by-iq-ix iq-ix) (fn [pos _ te-v2 [hp hp]]
        ; We need `[hp hp]` above to be sure we get a separate variable
        ; for each closure.
        [((get Tile.types "generator")
          :!pos
          :!hp
          :summon-class ~(get (.partition name " ") 2)
          :summon-hp (>> te-v2 5)
          :summon-frequency (get
            #(1 (f/ 1 2) (f/ 1 3) (f/ 1 4) (f/ 1 5) (f/ 1 6) (f/ 2 5) (f/ 1 10) (f/ 3 5) (+ 1 (f/ 1 3)) (+ 1 (f/ 1 2)) (+ 1 (f/ 2 3)) 2 (f/ 2 3) (f/ 3 4) (f/ 4 5) (f/ 5 6) (f/ 9 10))
              ; These come from IQ's `SetGenFreq`.
            (- (& te-v2 0b1111) 1)))])))))))

(defgenerated "o " "an orc" Approacher
  :iq-ix-mon [39 59 60] :iq-ix-gen [40 61 62]
  :points-mon 3 :points-gen 12

  :damage-melee #(3 6 9)
  :vampirizable T

  :flavor-mon "A green-skinned, muscle-bound, porcine humanoid with a pointy spear and a bad attitude."
  :flavor-gen "A sort of orcish clown car, facetiously called a village.")

(defgenerated "g " "a goblin" Approacher
  :iq-ix-mon [95 96 97] :iq-ix-gen [98 99 100]
  :points-mon 2 :points-gen 8

  :damage-melee #(2 4 6)
  :vampirizable T

  :flavor-mon "Goblins are a smaller, uglier, smellier, and worse-equipped cousin of orcs that try to make up for it with even more sadistic malice. It almost works."
  :flavor-gen "Oops, somebody gave the goblins a bath. Now there's a lot more of them, and they still stink.")

(defgenerated "G " "a ghost" Approacher
  :iq-ix-mon [37 55 56] :iq-ix-gen [38 57 58]
  :points-mon 5 :points-gen 25

  :immune undead-immunities
  :damage-melee #(5 10 15)
  :kamikaze T

  :flavor-mon "A spooky apparition bearing a striking resemblance to a man with a sheet draped over him. Giggle at your peril: it can discharge the negative energy that animates it to bring you closer to the grave yourself.\n\n    Lemme tell ya something: bustin' makes me feel good!"
  :flavor-gen "This big heap of human bones raises several questions, but sadly it appears you must treat the dead with even less respect in order to get rid of those ghosts.")

(defgenerated "b " "a bat" Wanderer
  :iq-ix-mon [45 71 72] :iq-ix-gen [46 73 74]
  :points-mon 1 :points-gen 3

  :damage-melee #(1 2 3)

  :flavor-mon "Dusk! With a creepy, tingling sensation, you hear the fluttering of leathery wings! Bats! With glowing red eyes and glistening fangs, these unspeakable giant bugs drop onto… wait. These aren't my lecture notes."
  :flavor-gen #[[A faint singing echoes out of the depths of this cave. They sound like they're saying "na na na".]])

(defgenerated "B " "a giant bee" Wanderer
  :iq-ix-mon [123 124 125] :iq-ix-gen [126 127 128]
  :points-mon 5 :points-gen 15

  :damage-melee #(5 7 9)

  :flavor-mon "Bees bafflingly being bigger'n bats. This is the kind that can survive stinging you. You might not be so lucky."
  :flavor-gen #[[The ancients call this place "the Plounge".]])

(defgenerated "d " "a devil" Approacher
  :iq-ix-mon [41 63 64] :iq-ix-gen [42 65 66]
  :points-mon 5 :points-gen 25

  :damage-melee #(3 6 9)
  :damage-shot 10

  :flavor-mon "A crimson-skinned, vaguely humanoid monster. Its eyes glow with the malevolent fires of hell, which it can hurl at you from a distance. Its claws are sharp, but don't hurt quite as much as getting roasted. To its enduring shame, it has no protection whatsoever against fire damage."
  :flavor-gen "A tunnel that goes all the way down to the Bad Place. It stinks of sulfur and invites the innumerable ill-spirited inhabitants of the inferno to ruin your day.")

(defgenerated "w " "a wizard" Approacher
  :iq-ix-mon [87 88 89] :iq-ix-gen [90 91 92]
  :points-mon 5 :points-gen 25

  :damage-melee 4
  :damage-shot #(4 8 12)
  :vampirizable T

  :flavor-mon "This fresh-faced would-be scholar has finished sewing the stars onto his robe and is starting to grow a beard. Idok has told the whole class that whoever kills you gets tenure. Considering what the rest of the academic job market is like, the offer has proven irresistible to many."
  :flavor-gen "The Pigpimples Institute of Thaumaturgy and Dweomercraft: a shameless diploma mill that happily takes students' money to teach them one spell, then sends them on a suicide mission against a much smarter and tougher opponent.")

(defgenerated "s " "a shade" Approacher
  :iq-ix-mon [171 172 173] :iq-ix-gen [174 175 176]
  :points-mon 6 :points-gen 24

  :immune #(MundaneArrow #* undead-immunities)
  :damage-melee #(3 5 7)

  :flavor-mon #[[A dark spirit with mastery of its semi-corporeal form, allowing ordinary arrows to pass right through it. As it approaches, it hisses "Death!"]]
  :flavor-gen "Oh dear. Considering what's been done to this grave, destroying it would be a mercy.")

(defgenerated "i " "an imp" [Approacher Wanderer]
  :iq-ix-mon [43 67 68] :iq-ix-gen [44 69 70]
  :points-mon 4 :points-gen 15

  :field-defaults (dict
    :shot-power (f/ 0))
  :mutable-fields #("shot_power")
  :info-bullets (meth []
    (.info-bullets (super)
      #("Shot power" @shot-power)))

  :damage-shot #(1 2 3)
  :$flee-range 2
  :$shot-frequency (f/ 4 5)

  :act (meth []
    (doc f"If the monster is within {@flee-range} squares of you, it flees (per `Approach` in reverse). Otherwise, if it has line of sight to you (ignoring all obstacles), it adds {@shot-frequency} to its shot power. If this is ≥1, it subtracts 1 to shoot you. Otherwise, it wanders (per `Wander`).")

    (when (and
        (<= (dist G.player.pos @pos) @flee-range)
        (not (@player-invisible-to?)))
      (return (@approach :reverse T :implicit-attack F)))
    (when (@try-to-attack-player :dry-run T :shots-ignore-obstacles T)
      (+= @shot-power @shot-frequency)
      (when (pop-integer-part @shot-power)
        (@try-to-attack-player :shots-ignore-obstacles T)
        (return)))
    (@wander :implicit-attack F))

  :flavor-mon #[[Weak but incredibly annoying, this snickering little fiend is called a "lobber" in the tongue of the ancients. It throws hellstones, cursed missiles that can pierce most any obstacle. In close quarters, it resorts to cowering helplessly and begging for mercy, but, being a literal demon, it has no compunctions about getting right back to firing at you the moment it feels safe.]]
  :flavor-gen "They don't make ziggurats like they used to.")

;; --------------------------------------------------------------
;; * Non-generated monsters
;; --------------------------------------------------------------

(deftile "T " "a thorn tree" Stationary
  :iq-ix 51
  :destruction-points 10

  :immune #(MundaneArrow MagicArrow Poison)
    ; We follow IQ in making thorn trees immune to poison, although
    ; the IQ manual suggests otherwise.
  :weaknesses #(Fire)
  :damage-melee 4

  :flavor "From a distance, you can safely giggle at the ghostly. Up close, this arboreal abomination will rake you with its twisted, spiny boughs. Arrows snag in its branches and glance off its gnarled bark, so an intimate encounter may be unavoidable. On the other hand, it's rather flammable. Remember, only you can start forest fires.")

(deftile "K " "a Dark Knight" Approacher
  :iq-ix 53
  :destruction-points 75

  :damage-melee 12

  :flavor "This dread warrior wears ink-black armor and carries a heavy chain mace. His devotion to the powers of evil (not to mention his willingness, nay, eagerness to kill you) makes his appropriation of Batman's epithet questionable at best. When you get down to it, he's just trying to distract you from the fact that he's the most basic enemy in the whole dungeon.")

(deftile "t " "a Tricorn" Approacher
  :iq-ix 54
  :destruction-points 10

  :damage-melee 5
  :damage-shot 6
  :shot-range 3

  :flavor "Named not for a hat, but for the three horns projecting from their equine heads, Tricorns spend decades mediating while cocooned in woolen blankets. Their richly cultivated spirituality allows them to unleash a spark of static electricity from a fair distance, albeit still not as far as your arrows can fly. Up close, they can poke you with their horns for slightly less damage.")

(deftile "A " "Death" Approacher
  :iq-ix 49
  :destruction-points 200

  :immune #(MundaneArrow Fire #* undead-immunities)
  :resists #(MagicArrow)
  :damage-melee 20

  :flavor "A shadowy hooded figure bearing a wicked scythe who speaks in all capital letters. It can be destroyed, but don't expect that to be easy.")

(deftile "N " "a negaton" Approacher
  :iq-ix 52
  :destruction-points 50

  :immune #(PlayerMelee MundaneArrow Fire Poison DeathMagic)
    ; The immunity to death magic is an addition compared to IQ. I
    ; added it because they're clearly not living things. "Killing"
    ; them with a wand of death makes no sense.
  :damage-melee 25
  :kamikaze T

  :flavor "A quantum of negative energy motivated only by a hatred of princess-based life forms. It can expend its entire payload in a single attack, and, being essentially mindless, it has no qualms about doing so. Magic arrows are pretty much the only thing strong enough to hurt it.")

(deftile "f " "a floater" Wanderer
  :iq-ix 47
  :destruction-points 2

  :damage-shot 10
  :shot-range 1
  :kamikaze T
  :$disturbance-increment (f/ 1 5)

  :act (meth []
    (doc f"If you're adjacent, increases your floater disturbance by {@disturbance-increment}. If your floater disturbance reaches 1, it's cleared and the monster attacks. Otherwise, the monster wanders per `Wander`.")
    (when (adjacent? @pos G.player.pos)
      (+= G.player.floater-disturbance @disturbance-increment)
      (when (pop-integer-part G.player.floater-disturbance)
        (return (@try-to-attack-player))))
    (@wander :implicit-attack F))

  :hook-destruction (meth [was-instakill?]
    "The monster can immediately attempt to attack, unless it killed itself by kamikaze."
    (unless was-instakill?
      (@try-to-attack-player)))

  :flavor "A giant aerial jellyfish, kept aloft by a foul-smelling and highly reactive gas. It doesn't fly so much as float about in the dungeon drafts. If disturbed, it readily explodes, and its explosions have the remarkable property of harming you and nobody else.")


(deftile "O " "a blob" [Summoner Wanderer]
  :iq-ix 48
  :destruction-points 3
  :score-for-damaging T
    ; In IQ, blobs are worth no points. I've given them points, but
    ; enabled `score-for-damaging` so you aren't penalized for killing
    ; them before they divide down to 1 HP.

  :immune #(MundaneArrow MagicArrow)
  :damage-melee 6
  :$summon-frequency (f/ 1 10)

  :act (meth []
    (doc f"If the monster can attack, it does. Otherwise, if it has more than 1 HP, it builds up {@summon-frequency} summoning power per turn. With enough power, it can split (per `Generate`) into two blobs with half HP (in case of odd HP, the original gets the leftover hit point). If it lacks the HP or summoning power for splitting, it wanders per `Wander`.")
    (when (@try-to-attack-player)
      (return))
    (when (and
        (> @hp 1)
        (@summon @stem @summon-frequency (// @hp 2)))
      (-= @hp (// @hp 2))
      (return))
    (@wander :implicit-attack F))

  :flavor "What looks like a big mobile puddle of slime is actually a man-sized amoeba. It retains the ability to divide (but not, fortunately, to grow), and its lack of distinct internal anatomy makes arrows pretty useless. It has just enough intelligence to notice that you're standing next to it and try to envelop you in its gloppy bulk.")


(deftile "s " "a gunk seed" Monster
  :color 'dark-orange
  :iq-ix 181
  :destruction-points 10

  :field-defaults (dict
    :growth-timer 5)
  :mutable-fields #("growth_timer")
  :suffix-dict (meth []
    (dict
      #** (.suffix-dict (super))
     :gt @growth-timer))
  :info-bullets (meth []
    (.info-bullets (super)
      #("Growth timer" @growth-timer)))

  :act (meth []
    "The monster's growth timer decreases by 1. If the timer has hit 0, it then transforms into an adult gunk."
    (-= @growth-timer 1)
    (when (= @growth-timer 0)
      (@replace "gunk")))

  :flavor "A seed of discord the size of a basketball that can flood a room inside of a minute. Think fast.")

(deftile "O " "a gunk" Summoner
  :color 'dark-orange
  :iq-ix 182
  :destruction-points 0

  :immune #(PlayerMelee MundaneArrow MagicArrow)
  :damage-melee 2

  :$summon-frequency (f/ 1 5)

  :act (meth []
    (doc f"If the monster can attack, it does. Otherwise, it builds up {@summon-frequency} summoning power per turn, which it can use to summon gunk seeds per `Generate`.")
    (or
      (@try-to-attack-player)
      (@summon :stem "gunk seed" :frequency @summon-frequency :hp 1)))

  :hook-destruction (meth [was-instakill?]
    "A gunk seed is created in its square."
    (unless was-instakill?
      (@replace "gunk seed")))

  :flavor "A peevish and very prolific pile of puke that pokes with pseudopods. It resists most weapons, and even if you do manage to kill it, it leaves a seed behind.")


(deftile "S " "a specter" Approacher
  :iq-ix 50
  :destruction-points 100

  :immune #(MundaneArrow #* undead-immunities)
  :damage-melee 15
  :sees-invisible T

  :act (meth []
     "Try to attack or approach per `Approach`. If that fails, try moving with a variation of `Approach` that allows skipping one intermediate tile."
     (or
       (@approach :advance-approach-dir F)
       (@approach :implicit-attack F :jump T)))

  :flavor "Yet another evil undead phantasm. This one's a real piece of work: it has a powerful heat-drain attack and the ability to teleport past obstacles.")


(deftile "S " "a giant spider" [Approacher Wanderer]
  :color 'brown
  :destruction-points 50

  :damage-melee 10
  :$approach-range 2

  :act (meth []
    (doc f"If the monster is within {@approach-range} squares of you, it approaches (per `Approach`). Otherwise, it wanders (per `Wander`). In both cases, it can move through webs, and it creates a web on its square afterwards if no web is there already.")
    ; Move or attack.
    (if (and
        (<= (dist G.player.pos @pos) @approach-range)
        (not (@player-invisible-to?)))
      (@approach :ethereal-to ["web"])
      (@wander :ethereal-to ["web"]))
    ; Spin a web in our new position, if there isn't one there
    ; already.
    (unless (any (gfor  tile (at @pos)  (= tile.stem "web")))
      (Tile.make @pos "web" :stack-ix (+ 1 (.index (at @pos) @)))))

  :flavor "This eight-legged beastie has powerful jaws, high-speed spinnerets, and the mark of a white skull embedded in the brown fur of its big fat abdomen. It's definitely giant and ambiguously intelligent, but not friendly or talkative.")
(setv (get Tile.types-by-iq-ix 135) (fn [pos _ te-v2]
  ; Unlike IQ, we represent the spider and its web separately.
  [
    ((get Tile.types "giant spider") :!pos :hp te-v2)
    ((get Tile.types "web") :!pos)]))


(deftile "Z " "a turret" Stationary
  :iq-ix 101
    ; This is called a "fire mage" in IQ. I've reflavored it to better
    ; fit the mechanics.
  :destruction-points 150
    ; In IQ, there's special code to give points for killing fire
    ; mages with a wand of annihilation, but they're worth 0 points,
    ; so it has no effect. I think managing to kill one should be
    ; rewarded.

  :immune #(PlayerMelee MundaneArrow MagicArrow Fire Poison)
  :damage-shot 10

  :flavor "A wretched organic structure, fashioned from fiendish flesh. It twists about to aim its toothy maw, from which it belches flame. It's immobile, but dark magics make it almost invulnerable… almost.")


(deftile "h " "a mind flayer" Approacher
  :iq-ix 185 ; Dark Brain
  :destruction-points 80

  :damage-melee 8
  :damage-shot 8
    ; Since mind flayers don't have Dark Brains' confusion attack,
    ; their shots always do damage.

  :flavor "A psychic monster from deep underground that can give you a wicked headache with telepathy, or tear off your scalp to reach your delicious brain with its tentacles.")


(deftile "W " "a blind mage" Approacher
  :color 'brown
  :iq-ix 166
  :destruction-points 75

  :damage-melee 4
  :damage-shot 8
    ; Again, without the special attack, shots always do damage.
  :sees-invisible T

  :flavor "An early-career researcher who has lost her powers of vision after countless hours of poring over manuscripts, memoranda, and prospective graduate students' letters of recommendation. She's had to develop acute hearing in order to detect the slightest whisper of new funding opportunities.")


(deftile "W " "a teleporting mage" Monster
  :color 'purple
  :iq-ix 186  ; invisible mage
  :destruction-points 100

  :field-defaults (dict
    :shot-power (f/ 0))
  :mutable-fields #("shot_power")
  :info-bullets (meth []
    (.info-bullets (super)
      #("Shot power" @shot-power)))

  :damage-shot 10
  :$shot-frequency (f/ 3 4)

  :act (meth []
    (doc f"If the monster has line of sight to you, it adds {@shot-frequency} to its shot power. If this is ≥1, it subtracts 1 to shoot you. If it doesn't shoot you, it tries to teleport into line of sight, preferring to be as close as possible to you without being adjacent. Its destination must lie in the reality bubble.")
    ; Teleporting mages' movement is much smarter than that of IQ's
    ; invisible mages, which compensates for the loss of their main
    ; ability.
    (when (@player-invisible-to?)
      (return))
    (when (@try-to-attack-player :dry-run T)
      (+= @shot-power @shot-frequency)
      (when (pop-integer-part @shot-power)
        (@try-to-attack-player)
        (return)))
    (for [
        dist-from-player [#* (thru 2 G.rules.reality-bubble-size) 1]
        direction Direction.all
        :if (setx target (.+n G.player.pos dist-from-player direction))]
      (when (and
          (or
            (= target @pos)
            (can-occupy? target :monster? T :ethereal-to #()))
          (@try-to-attack-player :dry-run T :pos target))
        (@move target)
        (return))))

  :flavor "This academic has perfected the art of avoiding faculty meetings, thesis committees, institutional review boards, classes, and his own office hours, preferring instead to transport himself to conferences in tropical destinations. His strategy for evaluating students (such as yourself) is to observe them from afar and see how they perform under pressure.")


(deftile "W " "an archmage" Approacher
  :iq-ix 163
  :destruction-points 75

  :damage-melee 2
  :damage-shot 12
  :sees-invisible T

  :special-shot (meth []
     (doc (.format "If possible, removes the first beneficial status effect that you have from the following list, instead of doing damage: {}."
       (.join ", " (gfor  e (StatusEffect.disenchantable)  e.name))))
     (StatusEffect.disenchant-player))

  :flavor "A professor emeritus whose killer instincts have been honed by decades of publishing and not perishing. His canny eye can detect the least visible academic politics, and his mastery of grant-review panels has bought him the reagents for powerful spells. But even with the best health insurance in the land, he's found that aging has taken its toll: he can no longer cane the young folk with the vigor of his early years.")


(deftile "a " "a giant ant" Approacher
  :iq-ix 184
  :destruction-points 50

  :damage-melee 7

  :special-melee (meth []
     (doc f"If you're not already paralyzed, you're paralyzed for {G.rules.paralysis-duration} turns.")
     (unless (.player-has? StatusEffect.Para)
       (.add StatusEffect.Para G.rules.paralysis-duration)
       T))

  :flavor "A belligerent reddish-brown bug the size of a cougar with a paralyzing venom and a strong work ethic. Oddly, giant spiders have no appetite for it.\n\n    I, for one, welcome our new insect overlords.")


(deftile "m " "a siren" Approacher
  :iq-ix 134
  :destruction-points 75

  :field-defaults (dict
    :shot-power (f/ 0))
  :mutable-fields #("shot_power")
  :info-bullets (meth []
    (.info-bullets (super)
      #("Shot power" @shot-power)))

  :damage-melee 5
  :$shot-frequency (f/ 1 4)

  :special-shot (meth []
     (doc f"If the monster can shoot at you and you're not already paralyzed, it gains {@shot-frequency} shot power. If this is ≥1, it can subtract 1 to paralyze you for {G.rules.paralysis-duration} turns.")
     (unless (.player-has? StatusEffect.Para)
       (+= @shot-power @shot-frequency)
       (when (pop-integer-part @shot-power)
         (.add StatusEffect.Para G.rules.paralysis-duration)
         T)))

  :flavor "This mermaid is all giggles and smiles, but she's obviously trying to kill you. She sings an enchanted song that can briefly enrapture you, holding you in place in a momentary crisis of conscience. The words go like this: \"Oh please, kind sir, spare me. Oh please, sir, get me back to the water. Let me live, oh let me live.\" Pretty rude of her to misgender you like that.\n\n    Hey guys, did you know that…")


(deftile "M " "a golem" Approacher
  :iq-ix 132
  :destruction-points 75

  :immune #(MundaneArrow Poison DeathMagic)
    ; Not immune to death magic in IQ, but seeing as they're
    ; nonliving, I think they ought to be.
  :damage-melee 18
  :$approach-range 3

  :act (meth []
    (doc f"If the monster is within {@approach-range} squares of you, it approaches (per `Approach`). Otherwise, it does nothing.")
    (when (and
        (<= (dist G.player.pos @pos) @approach-range)
        (not (@player-invisible-to?)))
      (@approach)))

  :flavor "An animated statue with dull senses and unbelievable strength.\n\n    I have a big ol' golem.\n    I made it out of clay.\n    And when it's dry and ready,\n    Oh people I shall slay.")


(deftile "C " "a cyclops" Approacher
  :iq-ix 164
  :destruction-points 100

  :immune #(PlayerMelee MundaneArrow MagicArrow)

  :flavor "A one-eyed gentle giant carrying a shield the size of a refrigerator, against which even magic arrows are useless. Abiding by a philosophy of nonviolent resistance against kyriarchy, he will do his best to obstruct you without hurting a hair on your head.")


(deftile "U " "an umber hulk" Wanderer
  :iq-ix 203 ; krogg
  :destruction-points 125
    ; That's 100 points from IQ, plus 25 points (10% of the value of a
    ; handful of gems) to make up for not actually dropping gems.

  :immune #(Fire)

  :damage-melee 10

  :act (meth []
    "As `Wander`, but if the selected square is impassable, the monster tries to destroy one tile on that square. A tile can be destroyed if it's permeable with a passwall amulet. If successful, the monster can try once more to move onto that square."
    (@wander :bump-hook @destroy-walls))

  :$destroy-walls (meth [target]
    (for [tile (at target)]
      (when (and (isinstance tile Scenery) tile.passwallable)
        ; We can destroy this tile. So we do, and then return, since
        ; we can only destroy one tile per turn.
        (.rm-from-map tile)
        (return))))

  :flavor "An umber hulk is something like a beetle with the frame of a particularly large gorilla. It can rapidly dig through solid rock, and its serrated mandibles can give you a nasty bite. This subspecies of umber hulk has gained an immunity to heat to adapt to the depths of planetary mantle it inhabits, but lost a (poorly thematically motivated) ancestral ability to magically confuse enemies with its gaze.")


(defclass Lord [Approacher Summoner]

  (setv
    summon-frequency NotImplemented
    summon-count 1
      ; Number of monsters generated per summon.
    summons NotImplemented)
      ; (stem, HP) pairs of monsters that can be summoned.

  (field-defaults
    summon-i 0)
  (setv mutable-fields #("summon_i"))
  (defmeth suffix-dict []
    (dict
      #** (.suffix-dict (super))
     :next (repr (get @summons @summon-i))))
  (defmeth info-bullets []
    (.info-bullets (super)
      #("Summoning frequency" @summon-frequency)
      #("Summoning count" @summon-count)
      #("Summons list" (repr (list @summons)))
      #("Next summon" (repr (get @summons @summon-i)))))

  (defmeth act []
    (doc f"Attack or Summon — If the monster can attack, it does. Otherwise, it builds up summoning power, which it can use to summon one or more monsters per `Generate`, drawing the next kind of summoned monster (and its HP) in order from its summons list. If it doesn't summon, it approaches (per `Approach`).")
    (or
      (@try-to-attack-player)
      (when (@try-summon @summon-frequency)
        ; When we have enough summoning power to summon at least one
        ; monster, then also summon any extras allowed by
        ; `@summon-count`. These new summons don't change summoning
        ; power on net.
        (do-n (- @summon-count 1)
          (@try-summon 1)))
      (@approach)))

   (defmeth try-summon [frequency]
     (setv [stem hp] (get @summons @summon-i))
     (when (@summon :!stem :!hp :!frequency)
       (setv @summon-i (% (+ @summon-i 1) (len @summons)))
       T)))

(deftile "d " "an archdevil" Lord
  :color 'red
  :bold T
  :iq-ix 129
  :destruction-points 90

  :damage-melee 12
  :damage-shot 15

  :summon-frequency (f/ 1 4)
  :summons #(#("devil" 1) #("devil" 2) #("devil" 3))

  :flavor "A bigger, badder devil with a long, pointy pitchfork. His authority puts innumerable rank-and-file devils at his disposal, but he's still not fireproof.\n\n    Please allow me to introduce myself.\n    I'm a man of wealth and taste.\n\n    PROTIP: To defeat the Cyberdemon, shoot at it until it dies.")

(deftile "L " "a Lord of the Undead" Lord
  :iq-ix 211
  :destruction-points 225

  ; In IQ, Lords of the Undead are immune to wands of death, but lack
  ; the usual undead immunity to poison, probably reflecting
  ; indecisiveness as to whether they're actually undead. We treat
  ; them as not undead.
  :damage-melee 15
  :damage-shot 5
    ; As with blind mages, shots always do damage.

  :summon-frequency (f/ 1 4)
  :summon-count 2
  :summons (tuple (gfor
    hp [1 2 3]
    stem ["ghost" "shade"]
    #(stem hp)))

  :flavor "A rare leathery-winged monster from some dark corner of the world. It can fire magic missiles at you, or call the spirits of the departed to attack you. It is not itself undead, which comes to show that the masses are all too often at the mercy of leaders who have nothing in common with them… something to think about, perhaps, Your Royal Highness?")

(deftile "K " "a Dark Princess" Lord
  :color 'red
  :bold T
  :iq-ix 165
    ; "Dark Prince" in IQ
  :destruction-points 125

  :damage-melee 15

  :summon-frequency (f/ 1 5)
  :summons #(#("Dark Knight" 6))

  :flavor #[[A feudal lord of Dark Knights. Her armor is covered with long spikes, and her massive halberd means business. When she sees you, she cries out "Fight me!". But first, she'd like to soften you up with some of her subordinates.]])


(deftile "V " "a vampire" [Wanderer Summoner]
  :iq-ix 204
  :destruction-points 100

  :field-defaults (dict
    :action-i 0)
  :mutable-fields #("action_i")

  :immune undead-immunities
  :damage-melee 10

  :$summon-frequency 2
  :$summon-hp 3
  :$action-list #(
    ; For simplicity, vampires don't also sometimes apporach as in IQ.
    'wander
    'wander
    'vampirize
    'wander
    'bats
    'vampirize
    'wander
    'wander
    'vampirize
    'bats)

  :info-bullets (meth []
    (.info-bullets (super)
      #("Action list" (.join ", " (map str @action-list)))
      #("Action index" @action-i)))

  :suffix-dict (meth []
    {
      #** (Monster.suffix-dict @)
      "wd" (:wd (Wanderer.suffix-dict @))
      ; Summoner.suffix-dict is skipped on purpose, because the
      ; displayed summon power will always be 0, because the summon
      ; frequency is an integer.
      "act" (hy.repr (str (get @action-list @action-i)))})

  :act (meth []
    (doc f"If the monster can attack, it does. Otherwise, it rotates among its list of actions. `wander` works per `Wander`. `bats` summons {@summon-frequency} bats, each with {@summon-hp} HP. `vampirize` attempts to turn an adjacent monster into a vampire, and works per `Wander` if no eligible monster is present.")
    (when (@try-to-attack-player)
      (return))
    (ecase (get @action-list @action-i)
      'wander
        (@wander)
      'bats
        (@summon "bat" @summon-frequency @summon-hp)
      'vampirize
        (block (for [p (burst @pos 1 :include-center F)  tile (at p)]
          (when (and
              (isinstance tile Monster)
              tile.vampirizable
              (in (get (walkability @pos (dir-to @pos p) :monster? T) 1)
                ['bump 'walk]))
            (.replace tile "vampire" :hp tile.hp)
            (block-ret))
          (else
            (@wander)))))
    (setv @action-i (% (+ 1 @action-i) (len @action-list))))

  :hook-destruction (meth [was-instakill?]
    (doc f"A bat with {@summon-hp} HP is created in its square.")
    (unless was-instakill?
      (@replace "bat" :hp @summon-hp)))

  :flavor "An aristocratic gentleman in a long black cloak with an infectious personality. A steady diet of the blood of the living makes him appear much more vivacious than other undead. Though he looks young, he is in fact somewhat long in the tooth.")


(deftile "@ " "a doppelganger" Approacher
  :iq-ix 177
  :destruction-points 100

  :damage-melee 5

  :$empathy-factor 5

  :hook-damaged (meth [amount]
    (doc f"For each point of damage the monster endures, you take {@empathy-factor} untyped damage.")
    ; In IQ, a ring of protection prevents this damage, but this is
    ; undocumented, and it feels unmotivated compared to the
    ; status-effect-themed effects of the ring.
    (.damage G.player (* amount @empathy-factor) :damage-type None))

  :flavor "Who is this amazingly good-looking woman? Her stiff, robotic movements make her too clumsy to use a bow, but you hate to see that beautiful face scratched. It feels personal. Maybe there's some way you can just take her out without having to give her a lot of unsightly wounds.")


(deftile "n " "a snitch" [Approacher Wanderer]
  :iq-ix 209
  :destruction-points 75
    ; Inexplicably worth no points in IQ, perhaps left over from a
    ; plan to make them drop extra treasure like Gauntlet's thief.

  :field-defaults (dict
    :item None
    :interest 0)
  :mutable-fields #("item" "interest")
  :suffix-dict (meth []
    (dict
      #** (.suffix-dict (super))
      :item (if @item @item.stem "---")
      :interest @interest))
  :info-bullets (meth [#* extra]
    (.info-bullets (super)
      #("Item" (and @item @item.full-name))
      #("Remaining interest in current item" @interest)))

  :immune #(MundaneArrow MagicArrow)
  :damage-melee 2
  :$sight-range 4
  :$initial-interest 5

  :$obtain (meth [item]
    (.move item None)
    (setv @item item)
    (setv @interest @initial-interest))

  :special-melee (meth []
    "The monster steals the last item in your inventory, or a key. You lose points for anything that's stolen."
    (for [[i item] (reversed (tuple (enumerate G.player.inventory)))]
      (when item
        (@obtain item)
        (setv (get G.player.inventory i) None)
        (break)))
    (when (and (not @item) G.player.keys)
      (@obtain ((get Tile.types "key")))
      (-= G.player.keys 1))
    (unless @item
      (return))
    (-= G.score @item.acquirement-points)
    T)

  :act (meth []
    (doc f"If the monster is within {@sight-range} squares, it approaches (per `Approach`) if empty-handed, and flees (per `Approach` in reverse) if it's carrying an item. Otherwise, it wanders (per `Wander`), taking any item it happens to step onto. It drops what it's holding if it gets a new item, or after {@initial-interest} steps of wandering.")
    (when (and
        (<= (dist G.player.pos @pos) @sight-range)
        (not (@player-invisible-to?)))
      (return (@approach #** (if @item
        (dict :reverse T :implicit-attack F)
        {}))))
    (setv p-was @pos)
    (setv item-was @item)
    (@wander :bump-hook @pick-up-item)
    (when (and @item (!= @pos p-was)) (cond
      (is @item item-was) (do
        (-= @interest 1)
        (when (= @interest 0)
          (.move @item p-was)
          (setv @item None)
          (setv @interest None)))
      item-was
        (.move item-was p-was))))

  :$pick-up-item (meth [target]
    (for [tile (at target)]
      (when (isinstance tile hy.I.simalq/tile.Item)
        (@obtain tile)
        (return))))

  :hook-destruction (meth [was-instakill?]
    (doc "The monster drops what it's holding, even if it was instakilled.")
    (when @item
      (.move @item @pos)))

  :flavor #[[Described aptly by the sages as "greedy little pests", snitches are small green men that like to acquire things, particularly things in other people's pockets. Their quick hands can seize arrows midflight and relieve sharp-eyed princesses of their belongings. They're just as quick to grow bored of their loot and search for new treasures.]])


(defclass Dragon [Approacher]

  (field-defaults
    regen-power 0)
  (setv mutable-fields #("regen_power"))

  (setv
    regen-frequency NotImplemented
    grow-threshold None
    grow-stem None
    regen-limit 16)

  (defmeth suffix-dict []
    (dict
      #** (.suffix-dict (super))
      :pw @regen-power))
  (defmeth info-bullets []
    (.info-bullets (super)
      #("Regeneration power" @regen-power)
      #("Regeneration frequency" @regen-frequency)
      #("Growth threshold" @grow-threshold)
      #("Next life stage" @grow-stem)))

  (setv grow-help "adds its regeneration frequency to its regeneration power. If the sum is ≥1, the integer part is removed to add to the monster's HP. Then, if the monster has a growth threshold and its HP is greater or equal, it advances to its next life stage (and loses all regeneration power).")

  (defmeth act []
    (doc f"Approach and Grow — The monster approaches per `Approach`. Then, it {@grow-help}")
    (@approach)
    (@regen))

  (defmeth regen []
    (+= @regen-power @regen-frequency)
    (setv @hp (max
      @hp
      (min @regen-limit (+ @hp (pop-integer-part @regen-power)))))
    (when (and (is-not @grow-threshold None) (>= @hp @grow-threshold))
      (@replace @grow-stem :hp @hp)))

  (setv flavor "Dragons are very, very large reptiles that hatch from eggs and grow stronger at an alarming rate. Their claws are razor-sharp from birth. As an adult, they can spew gouts of super-hot flame.\n\n    Do not meddle in the affairs of dragons, for you are crunchy and taste good with ketchup."))

(deftile "e " "a dragon egg" Dragon
  :iq-ix 195
  :destruction-points 20

  :regen-frequency (f/ 4 5)
  :grow-threshold 4
  :grow-stem "wyrmling"

  :act (meth []
    (doc f"The monster {@grow-help}")
    (@regen)))

(deftile "D " "a wyrmling" Dragon
  :color 'brown
  :iq-ix 196
    ; Renamed from IQ's "wyrm" to make its youth more obvious.
  :destruction-points 50

  :damage-melee 8

  :regen-frequency (f/ 3 5)
  :grow-threshold 8
  :grow-stem "dragon")

(deftile "D " "a dragon" Dragon
  :iq-ix 197

  :damage-melee 20
  :damage-shot 20

  :regen-frequency (f/ 2 5)
  :destruction-points 250)


)
