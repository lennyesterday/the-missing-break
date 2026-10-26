"""Streamlit screens only, no game rules."""

from pathlib import Path

import streamlit as st

import db
import logic

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="The Missing Break")

# Clickable graffiti screens (home, intro). Every element with data-action is a button;
# clicking an enabled one sends its action back to Python as the "clicked" trigger.
SVG_SCREEN_JS = """
export default function (component) {
    const { data, parentElement, setTriggerValue } = component;
    // The graffiti fonts (static/fonts, served by Streamlit), added to the page once.
    if (!document.getElementById("graffiti-fonts")) {
        const fonts = document.createElement("style");
        fonts.id = "graffiti-fonts";
        fonts.textContent =
            "@font-face { font-family: 'Sedgwick Ave Display'; src: url('app/static/fonts/SedgwickAveDisplay-Regular.ttf') format('truetype'); }" +
            "@font-face { font-family: 'Sedgwick Ave'; src: url('app/static/fonts/SedgwickAve-Regular.ttf') format('truetype'); }";
        document.head.appendChild(fonts);
    }
    let root = parentElement.querySelector(".svg-screen");
    if (!root) {
        root = document.createElement("div");
        root.className = "svg-screen";
        parentElement.appendChild(root);
    }
    // nonce: the same picture again from the start (e.g. the same move twice in a row)
    const svgKey = data.file + ":" + data.svg.length + ":" + (data.nonce || "");
    if (root.dataset.svgKey !== svgKey) {
        // the sounds of the old picture's parts (a shot on the court) stop with it
        const old = window.__goodfellasSound;
        if (old && old.parts) { old.parts.forEach((p) => p.pause()); old.parts = []; }
        root.innerHTML = data.svg;
        root.dataset.svgKey = svgKey;
        delete root.dataset.playing;  // a new picture: its door can be clicked again
        // An inserted SVG shares the page's animation clock: restart it so the animation plays from the start.
        // data-sync="audio": instead, put it where the music is in its loop (data-loop seconds long),
        // so the picture keeps time with the music (e.g. the practice decks switch on the loop's restart).
        const svg = root.querySelector("svg");
        const music = window.__goodfellasSound && window.__goodfellasSound.player;
        if (svg && svg.setCurrentTime) {
            const synced = svg.dataset.sync === "audio" && music && !music.paused;
            svg.setCurrentTime(synced ? music.currentTime % parseFloat(svg.dataset.loop || "1") : 0);
        }
        delete root.dataset.skipped;
    }
    // SKIP: jump to the end of the animation (once per picture).
    if (data.seek_end && root.dataset.skipped !== svgKey) {
        const svg = root.querySelector("svg");
        if (svg && svg.setCurrentTime) svg.setCurrentTime(parseFloat(svg.getAttribute("data-end") || "0"));
        root.dataset.skipped = svgKey;
    }
    // Sound: one player for the whole page. data.audio = {src, id} starts a song, once per id.
    const sound = window.__goodfellasSound || (window.__goodfellasSound = { player: new Audio(), last: null });
    const isMuted = () => { try { return localStorage.getItem("goodfellas-muted") === "1"; } catch (e) { return false; } };
    sound.player.muted = isMuted();
    if (data.audio && data.audio.id !== sound.last) {
        sound.last = data.audio.id;
        if (data.audio.cmd === "fade") {  // fade the song out over 2 s, then stop it
            const player = sound.player;
            clearInterval(player.__fade);
            player.__fade = setInterval(() => {
                player.volume = Math.max(0, player.volume - 0.025);
                if (player.volume === 0) { clearInterval(player.__fade); player.pause(); player.volume = 1; }
            }, 50);
        } else if (data.audio.cmd === "pause") {
            sound.player.pause();  // keeps its place
        } else if (data.audio.cmd === "resume") {
            sound.player.play().catch(() => {});  // goes on from there
        } else if (data.audio.src) {
            clearInterval(sound.player.__fade);  // a new song: at full volume
            sound.player.volume = 1;
            sound.player.src = data.audio.src;
            sound.player.loop = !!data.audio.loop;  // e.g. the drum break: round and round
            sound.player.currentTime = 0;
            sound.player.play().catch(() => {});
        } else {
            sound.player.pause();  // {src: null}: stop the song
        }
        // audio.end: the click to make when the song is over (e.g. the next rapper's turn)
        const end = data.audio.src ? data.audio.end : null;
        sound.player.onended = end ? () => sound.trigger && sound.trigger("clicked", end) : null;
    }
    sound.trigger = setTriggerValue;  // the picture on the page now
    // The background sound of a scene: a second player that loops. data.ambience is its src while
    // the scene is shown, or null; it fades in and out instead of starting and stopping hard.
    if (!sound.ambience) {
        sound.ambience = new Audio();
        sound.ambience.loop = true;
        sound.ambience.volume = 0;
    }
    const amb = sound.ambience;
    amb.muted = isMuted();
    const fadeTo = (target, secs) => {
        clearInterval(amb.__fade);
        const step = (target - amb.volume) / Math.max(1, secs * 20);
        amb.__fade = setInterval(() => {
            const next = amb.volume + step;
            if ((step >= 0 && next >= target) || (step < 0 && next <= target)) {
                amb.volume = target;
                clearInterval(amb.__fade);
                if (target === 0) amb.pause();
            } else {
                amb.volume = next;
            }
        }, 50);
    };
    // Browsers only play sound after the player has clicked or pressed a key on the page: if
    // playing is blocked, try again on the first click or key press.
    const start = () => amb.play().catch(() => {
        if (amb.__waiting) return;
        amb.__waiting = true;
        const retry = () => {
            amb.__waiting = false;
            document.removeEventListener("pointerdown", retry, true);
            document.removeEventListener("keydown", retry, true);
            if (amb.__target > 0) amb.play().catch(() => {});
        };
        document.addEventListener("pointerdown", retry, true);
        document.addEventListener("keydown", retry, true);
    });
    const volume = data.ambience_volume || 0.45;
    if (data.ambience) {
        if (amb.src && !amb.src.endsWith(data.ambience) && !amb.paused && amb.volume > 0) {
            // another sound is playing (e.g. the intro song): fade it out, then switch
            amb.__target = -1;
            fadeTo(0, 1);
            clearTimeout(amb.__switch);
            amb.__switch = setTimeout(() => {
                amb.src = data.ambience;
                amb.volume = 0;
                amb.__target = volume;
                start();
                fadeTo(volume, 1.5);
            }, 1100);
        } else if (amb.__target !== volume && amb.__target !== -1) {
            if (!amb.src.endsWith(data.ambience)) { amb.src = data.ambience; amb.volume = 0; }
            amb.__target = volume;
            if (amb.paused) start();
            fadeTo(volume, 1.5);
        }
    } else if (amb.__target !== 0) {
        clearTimeout(amb.__switch);
        amb.__target = 0;
        fadeTo(0, 1.5);
    }
    // The crew's voices: data.voice = {src, id} plays a line once (per id); the background sound
    // gets quieter while someone speaks. Without data.voice nobody speaks. data.voice.delay: it
    // waits that many seconds first (a line said during a walk, when its bubble shows).
    if (!sound.voice) sound.voice = new Audio();
    const voice = sound.voice;
    voice.muted = isMuted();
    if (data.voice && data.voice.id !== sound.lastVoice) {
        sound.lastVoice = data.voice.id;
        clearTimeout(sound.voiceTimer);
        voice.pause();
        const speak = () => {
            voice.src = data.voice.src;
            voice.currentTime = 0;
            voice.play().then(() => {
                if (amb.__target > 0) fadeTo(amb.__target * 0.35, 0.3);
            }).catch(() => {});
            voice.onended = () => { if (amb.__target > 0) fadeTo(amb.__target, 0.8); };
        };
        if (data.voice.delay) sound.voiceTimer = setTimeout(speak, 1000 * data.voice.delay);
        else speak();
    } else if (!data.voice) {
        clearTimeout(sound.voiceTimer);  // (e.g. SKIP before a walk's line)
        sound.lastVoice = null;
        if (!voice.paused) {
            voice.pause();
            if (amb.__target > 0) fadeTo(amb.__target, 0.8);
        }
    }
    // Sound effects that go with an animation (the intro): the svg's data-cues lists for each sound
    // when it plays ({src, on: [[from, to], ...], vol, resume}). They follow the picture's own clock,
    // so SKIP (which jumps to the end) silences them, and they stop when the picture goes away.
    const clearCues = () => {
        if (!sound.cues) return;
        clearInterval(sound.cues.timer);
        sound.cues.players.forEach((p) => { clearInterval(p.__fade); p.pause(); });
        sound.cues = null;
    };
    const cuePicture = root.querySelector("svg");
    if (!cuePicture || !cuePicture.dataset.cues) {
        clearCues();
    } else if (!sound.cues || sound.cues.key !== svgKey || !sound.cues.svg.isConnected) {
        clearCues();
        const cues = JSON.parse(cuePicture.dataset.cues);
        const players = cues.map((cue) => {
            const p = new Audio(cue.src);
            p.loop = !!cue.resume;
            p.volume = 0;
            p.muted = isMuted();
            return p;
        });
        const fade = (p, target, secs) => {
            clearInterval(p.__fade);
            const step = (target - p.volume) / Math.max(1, secs * 20);
            p.__fade = setInterval(() => {
                const next = p.volume + step;
                if ((step >= 0 && next >= target) || (step < 0 && next <= target)) {
                    p.volume = Math.max(0, Math.min(1, target));
                    clearInterval(p.__fade);
                    if (target === 0) p.pause();
                } else {
                    p.volume = Math.max(0, Math.min(1, next));
                }
            }, 50);
        };
        const tick = () => {
            if (!cuePicture.isConnected) { clearCues(); return; }  // (the picture sits in a shadow root, so ask the picture itself)
            const t = cuePicture.getCurrentTime();
            const paused = cuePicture.animationsPaused && cuePicture.animationsPaused();
            cues.forEach((cue, i) => {
                const p = players[i];
                p.muted = isMuted();
                // every: the cue comes round again every this many seconds (the train on the block)
                const ct = cue.every ? t % cue.every : t;
                const now = !paused && cue.on.find(([a, b]) => ct >= a && ct < b);
                if (now && !p.__on) {
                    p.__on = true;
                    if (!cue.resume) p.currentTime = Math.max(0, ct - now[0]);  // from where the action is
                    p.play().catch(() => {});
                    fade(p, cue.vol, 0.15);
                } else if (now && p.paused && !p.__trying) {
                    // the browser blocked it (no click on the page yet): keep trying, it starts after one
                    p.__trying = true;
                    p.play().catch(() => {}).finally(() => { p.__trying = false; });
                } else if (!now && p.__on) {
                    p.__on = false;
                    fade(p, 0, 0.15);
                }
            });
        };
        sound.cues = { key: svgKey, svg: cuePicture, players, timer: setInterval(tick, 50) };
    }
    // A picture that goes on by itself: data-auto-action on the svg happens when the picture's own
    // clock reaches data-auto-delay (so it waits while the animation is paused or the tab is hidden).
    clearInterval(root.__autoTimer);
    if (cuePicture && cuePicture.dataset.autoAction && root.dataset.autoDone !== svgKey) {
        const delay = parseFloat(cuePicture.dataset.autoDelay || "0");
        root.__autoTimer = setInterval(() => {
            if (!cuePicture.isConnected) { clearInterval(root.__autoTimer); return; }
            if (cuePicture.getCurrentTime() >= delay) {
                clearInterval(root.__autoTimer);
                root.dataset.autoDone = svgKey;
                // a deferred press (data-defer) happens now, at the end; otherwise the picture's own action
                const action = root.__deferred || cuePicture.dataset.autoAction;
                // data-pause-on: this action stops the music right now, on the beat (e.g. the hand
                // stopping the record to mark it), before the page even hears about it
                if (action === cuePicture.dataset.pauseOn && sound.player) sound.player.pause();
                setTriggerValue("clicked", action);
                root.__deferred = null;
            }
        }, 100);
    }
    // the sound switch, top right of every picture
    root.style.position = "relative";
    let toggle = root.querySelector(".sound-toggle");
    if (!toggle) {
        toggle = document.createElement("button");
        toggle.className = "sound-toggle";
        toggle.setAttribute("aria-label", "Sound on or off");
        root.appendChild(toggle);
    }
    toggle.textContent = isMuted() ? "🔇" : "🔊";
    toggle.onclick = () => {
        const muted = !isMuted();
        try { localStorage.setItem("goodfellas-muted", muted ? "1" : "0"); } catch (e) {}
        sound.player.muted = muted;
        amb.muted = muted;
        voice.muted = muted;
        if (sound.cues) sound.cues.players.forEach((p) => { p.muted = muted; });
        (sound.parts || []).forEach((p) => { p.muted = muted; });
        toggle.textContent = muted ? "🔇" : "🔊";
    };
    // the crew's backpack, top right next to the sound switch in the scene pictures and walks: opens what the crew carries
    // over the picture. Only for looking: no click goes back to the app, nothing is saved.
    let pack = root.querySelector(".backpack-button");
    let panel = root.querySelector(".backpack-panel");
    if (!data.backpack) {
        if (pack) { pack.remove(); panel.remove(); }
    } else {
        if (!pack) {
            pack = document.createElement("button");
            pack.className = "backpack-button";
            pack.setAttribute("aria-label", "Open the backpack");
            root.appendChild(pack);
            panel = document.createElement("div");
            panel.className = "backpack-panel";
            panel.hidden = true;
            root.appendChild(panel);
            const setOpen = (open) => {
                panel.hidden = !open;
                pack.setAttribute("aria-expanded", String(open));
                if (open) panel.querySelector(".backpack-close").focus();
            };
            root.__setBackpack = setOpen;
            pack.onclick = () => setOpen(panel.hidden);
            panel.onclick = (e) => { if (e.target === panel || e.target.closest(".backpack-close")) setOpen(false); };
            panel.onkeydown = (e) => { if (e.key === "Escape") { setOpen(false); pack.focus(); } };
        }
        const items = data.backpack.items;
        pack.innerHTML = "🎒" + (items.length ? `<span class="backpack-count">${items.length}</span>` : "");
        const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
        panel.innerHTML = `<div class="backpack-box" role="dialog" aria-label="Backpack">
            <button class="backpack-close" aria-label="Close the backpack">✕</button>
            <div class="backpack-title">BACKPACK</div>` +
            (items.length
                ? "<ul>" + items.map((i) => `<li><span class="backpack-icon">${i.icon}</span>${esc(i.name)}</li>`).join("") + "</ul>"
                : `<div class="backpack-empty">EMPTY. NOTHING IN HERE YET.</div>`) +
            `<div class="backpack-cash">CASH: ${esc(data.backpack.cash)}</div></div>`;
        if (root.__backpackKey !== svgKey) root.__setBackpack(false);  // a new picture: the backpack closes
        root.__backpackKey = svgKey;
    }
    // Parts of the picture that come and go. data-overlay lists names: a part shows while all its
    // names are in data.show, and none of its "!names". When a part comes up, its animations marked
    // begin="indefinite" start right then (e.g. Bible walking to the mic).
    const shown = data.show || [];
    root.querySelectorAll("[data-overlay]").forEach((overlay) => {
        const visible = overlay.dataset.overlay.split(" ").every((name) =>
            name.startsWith("!") ? !shown.includes(name.slice(1)) : shown.includes(name));
        const wasVisible = overlay.style.display !== "none";
        overlay.style.display = visible ? "" : "none";
        if (visible && !wasVisible) {
            overlay.querySelectorAll('[begin="indefinite"]').forEach((anim) => {
                try { anim.beginElement(); } catch (e) {}
            });
            // a part can bring its own sound (a shot on the court): it plays once, from the start
            if (overlay.dataset.sound) {
                if (overlay.__sound) overlay.__sound.pause();
                const p = new Audio(overlay.dataset.sound);
                p.volume = parseFloat(overlay.dataset.soundVolume || "0.8");
                p.muted = isMuted();
                p.play().catch(() => {});
                overlay.__sound = p;
                sound.parts = (sound.parts || []).filter((q) => !q.paused).concat([p]);
            }
            // a part can go on by itself: data-auto-action after data-auto-delay seconds
            const auto = overlay.dataset.autoAction;
            if (auto) {
                clearTimeout(overlay.__autoTimer);
                overlay.__autoTimer = setTimeout(() => {
                    if (overlay.style.display !== "none") setTriggerValue("clicked", auto);
                }, 1000 * parseFloat(overlay.dataset.autoDelay || "0"));
            }
        }
        if (!visible) {
            clearTimeout(overlay.__autoTimer);
            if (overlay.__sound) { overlay.__sound.pause(); overlay.__sound = null; }
        }
    });
    const picture = root.querySelector("svg");
    if (picture && picture.pauseAnimations) {
        if (shown.includes("paused")) picture.pauseAnimations();
        else if (picture.animationsPaused()) picture.unpauseAnimations();
    }
    root.querySelectorAll("[data-action]").forEach((button) => {
        const action = button.dataset.action;
        const enabled = data.enabled.includes(action);
        button.classList.toggle("disabled", !enabled);
        button.setAttribute("aria-disabled", String(!enabled));
        // data-defer: the press is only noted (shown at once with data-pressed) and happens when the
        // picture's time is up (e.g. SPIN BACK switches the decks right on the loop's restart)
        const press = () => {
            if (!enabled) return;
            // data-plays: the click first plays an animation in the picture (e.g. the crew going in
            // through the door) and only does its action after data-action-delay seconds, if the
            // picture is still there (not if SKIP has moved on)
            if (button.dataset.plays) {
                if (root.dataset.playing === svgKey) return;  // once
                root.dataset.playing = svgKey;
                const pic = root.querySelector("svg");
                const anim = root.querySelector(`#${button.dataset.plays}`);
                try { anim.beginElement(); } catch (e) {}
                setTimeout(() => {
                    if (root.querySelector("svg") === pic && pic.isConnected) setTriggerValue("clicked", action);
                }, 1000 * parseFloat(button.dataset.actionDelay || "0"));
                return;
            }
            if (button.dataset.defer) {
                if (root.__deferred) return;  // one press per round
                root.__deferred = action;
                const pic = root.querySelector("svg");
                if (pic) pic.setAttribute("data-pressed", action);
            } else {
                setTriggerValue("clicked", action);
            }
        };
        button.onclick = press;
        button.onkeydown = (e) => {
            if (e.key === "Enter" || e.key === " ") { e.preventDefault(); press(); }
        };
    });
    // A record plays only while its turntable is on the page: when the turntable view goes away
    // (whatever the reason), its song stops.
    if (data.file && data.file.startsWith("assets/records/")) {
        return () => setTimeout(() => {
            if (!document.contains(root)) sound.player.pause();
        }, 0);
    }
}
"""

SVG_SCREEN_CSS = """
.svg-screen svg { width: 100%; height: auto; display: block; }
[data-action] { cursor: pointer; transition: filter 0.15s; outline: none; }
[data-action]:hover, [data-action]:focus-visible { filter: brightness(1.15) drop-shadow(0 0 8px #ffd23f); }
[data-action].disabled { cursor: not-allowed; filter: grayscale(1) brightness(0.75); }
svg[data-pressed="loop_hit"] .press-hit, svg[data-pressed="loop_miss"] .press-miss { display: inline !important; }
svg[data-pressed] [data-defer] { opacity: 0.45; pointer-events: none; }
/* point and click: a way out lights up under the pointer and shows where it leads; on touch
   screens (no pointer to hover with) the labels always show */
.exit .exit-label { opacity: 0; transition: opacity 0.15s; pointer-events: none; }
.exit:hover .exit-label, .exit:focus-visible .exit-label { opacity: 1; }
.exit .exit-area { transition: fill-opacity 0.15s; }
.exit:hover .exit-area, .exit:focus-visible .exit-area { fill-opacity: 0.18; }
@media (hover: none) { .exit .exit-label { opacity: 0.9; } }
.sound-toggle { position: absolute; top: 8px; right: 8px; width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid #f4f4f4; background: rgba(17, 17, 17, 0.8); font-size: 17px; cursor: pointer; line-height: 1; }
.backpack-button { position: absolute; top: 8px; right: 52px; width: 36px; height: 36px; padding: 0; border-radius: 50%;
  border: 2px solid #ffd23f; background: rgba(17, 17, 17, 0.8); font-size: 18px; cursor: pointer; line-height: 1;
  transition: transform 0.15s, filter 0.15s; }
.backpack-button:hover, .backpack-button:focus-visible { transform: rotate(-8deg) scale(1.08); filter: drop-shadow(0 0 8px #ffd23f); outline: none; }
.backpack-count { position: absolute; right: -6px; bottom: -6px; min-width: 20px; height: 20px; padding: 0 4px; box-sizing: border-box;
  border-radius: 10px; border: 2px solid #111; background: #e8336f; color: #fff; font: bold 12px/16px sans-serif; }
.backpack-panel { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.55); }
.backpack-panel[hidden] { display: none; }
.backpack-box { position: relative; min-width: 260px; max-width: 80%; max-height: 80%; overflow-y: auto; padding: 18px 26px 16px;
  background: #1b1b1f; border: 4px solid #ffd23f; border-radius: 14px; box-shadow: 6px 6px 0 #e8336f; color: #f4f4f4;
  transform: rotate(-1.5deg); font: bold 15px sans-serif; }
.backpack-title { font: 34px 'Sedgwick Ave Display', sans-serif; color: #ffd23f; text-shadow: 3px 3px 0 #e8336f, -1px -1px 0 #111;
  margin: 0 30px 10px 0; letter-spacing: 1px; }
.backpack-box ul { list-style: none; margin: 0; padding: 0; }
.backpack-box li { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-bottom: 2px dashed #444; }
.backpack-icon { font-size: 24px; width: 30px; text-align: center; }
.backpack-empty { padding: 10px 0; color: #aaa; }
.backpack-cash { margin-top: 12px; color: #7ee081; }
.backpack-close { position: absolute; top: 10px; right: 10px; width: 30px; height: 30px; border-radius: 50%;
  border: 2px solid #f4f4f4; background: #333; color: #f4f4f4; font-size: 15px; cursor: pointer; }
"""

svg_screen_component = st.components.v2.component("svg_screen", js=SVG_SCREEN_JS, css=SVG_SCREEN_CSS)


def svg_screen(name, svg_file, enabled, show=(), seek_end=False, audio=None, ambience=None, voice=None, nonce=None,
               backpack=None):
    """Show a clickable graffiti screen and return the action the player clicked, if any.

    enabled: the data-action buttons that work. show: the data-overlay parts to show.
    seek_end: jump to the end of the animation (SKIP). audio: a song to play ({src, id}).
    ambience: the background sound to loop while this screen is shown (a SONGS id), or None.
    voice: a line of dialogue to speak ({src, id}), or None.
    backpack: what the crew carries, for the 🎒 button (see backpack()), or None for no button.
    Tests hand in the same value as session_state[f"{name}_choice"].
    """
    svg = (APP_DIR / svg_file).read_text()
    result = svg_screen_component(
        key=name,
        data={"svg": svg, "file": svg_file, "enabled": list(enabled), "show": list(show), "seek_end": seek_end,
              "audio": audio, "ambience": f"app/static/{logic.SONGS[ambience]['file']}" if ambience else None,
              "ambience_volume": logic.SONGS[ambience].get("volume", 0.45) if ambience else 0,
              "voice": voice, "nonce": nonce, "backpack": backpack},
        on_clicked_change=lambda: None,
    )
    if result.clicked:
        st.session_state[f"{name}_choice"] = result.clicked
    return st.session_state.pop(f"{name}_choice", None)


def walk_file(from_scene, to_scene):
    """The crew's walking animation for this route, or None if there is none."""
    path = f"assets/walks/{from_scene}__{to_scene}.svg"
    return path if (APP_DIR / path).is_file() else None


def scene_file(scene_id):
    """The scene's picture, or None if it has none yet."""
    path = f"assets/scenes/{scene_id}.svg"
    return path if (APP_DIR / path).is_file() else None


def start_new_game():
    st.session_state.game = logic.new_game()
    db.save_game(db.db_path(), st.session_state.game)
    st.session_state.feedback = None
    st.session_state.walk = None
    st.session_state.show_intro = True  # Portals sprays the story first
    st.session_state.intro_skipped = False
    st.session_state.show_escape = False
    st.session_state.talk = {}  # how far each scene's conversation has got
    st.session_state.rapping = []
    st.session_state.looking_at = None
    st.session_state.in_cypher = False
    st.session_state.practicing = None
    st.session_state.tried_before = None  # nothing was just turned down
    st.session_state.came_from = None  # nor did the crew just come from anywhere
    st.session_state.just_did = None  # nor do anything
    st.session_state.just_turned_down = None


def resume_game():
    st.session_state.game = db.load_game(db.db_path())
    st.session_state.feedback = None
    st.session_state.walk = None
    st.session_state.show_intro = False
    st.session_state.show_escape = False
    st.session_state.in_cypher = False
    st.session_state.practicing = None
    st.session_state.tried_before = None  # nothing was just turned down
    st.session_state.came_from = None  # nor did the crew just come from anywhere
    st.session_state.just_did = None  # nor do anything
    st.session_state.just_turned_down = None


def do_action(action_id):
    before = st.session_state.game.current_scene
    happens = logic.what_happens(st.session_state.game, action_id) or {}
    result = logic.apply_action(st.session_state.game, action_id)
    st.session_state.walk = None
    if result.accepted:
        st.session_state.game = result.state
        db.save_game(db.db_path(), result.state)
        # a picture can show what just happened (e.g. "you got the key")
        st.session_state.last_done = happens.get("done", action_id) if result.message else None
        st.session_state.last_rejected = None
        st.session_state.just_did = action_id  # (not saved: e.g. Needle has just practiced)
        if result.state.current_scene != before:
            st.session_state.walk = walk_file(before, result.state.current_scene)
            # coming back: the reminder plays again each time
            for kind in ("back", "after", "won"):
                st.session_state.setdefault("talk", {}).pop(f"{result.state.current_scene}:{kind}", None)
            st.session_state.arrivals = st.session_state.get("arrivals", 0) + 1
            # what was just turned down where the crew came from (e.g. the gate): the place they get
            # to can answer it, only now (not saved: being turned down is not a move)
            st.session_state.tried_before = st.session_state.get("just_turned_down")
            st.session_state.came_from = before  # (not saved either: after a restart they're just there)
            stop_rapping()  # leaving the station: the verse stops
        st.session_state.just_turned_down = None
        if happens.get("raps"):
            start_rapping(happens["raps"])
    else:
        # ... or why it didn't work (e.g. "the gate is chained shut")
        st.session_state.last_rejected = action_id
        st.session_state.just_turned_down = action_id
        st.session_state.turned_down = st.session_state.get("turned_down", 0) + 1
    st.session_state.feedback = (result.accepted, result.message)


def handle_home_choice(choice):
    confirming = st.session_state.get("confirm_restart", False)
    outcome = logic.home_choice(choice, db.has_save(db.db_path()), confirming)
    if outcome == "new_game":
        st.session_state.confirm_restart = False
        start_new_game()
    elif outcome == "confirm_restart":
        st.session_state.confirm_restart = True
    elif outcome == "cancel":
        st.session_state.confirm_restart = False
    elif outcome == "resume":
        resume_game()


def show_menu():
    has_save = db.has_save(db.db_path())
    if st.session_state.get("confirm_restart"):
        enabled, show = ["restart_yes", "restart_no"], ["confirm-restart"]
    else:
        enabled, show = (["start", "resume"] if has_save else ["start"]), []
    choice = svg_screen("home", "assets/screens/home.svg", enabled, show, ambience=logic.INTRO_MUSIC)
    if choice:
        handle_home_choice(choice)
        st.rerun()


def show_intro():
    skipped = st.session_state.get("intro_skipped", False)
    choice = svg_screen("intro", "assets/screens/intro.svg", ["go", "skip"], seek_end=skipped, ambience=logic.INTRO_MUSIC)
    if choice == "go":
        st.session_state.show_intro = False
        st.session_state.show_escape = True  # Portals escapes through a portal into the basement
        st.rerun()
    elif choice == "skip":
        st.session_state.intro_skipped = True
        st.rerun()


def show_escape():
    """Between the intro and the basement: Portals escapes the police through a portal. It goes
    on to the basement by itself when it is over (or with SKIP)."""
    # no ambience: the intro song fades out as soon as LET'S GO is pressed
    choice = svg_screen("escape", "assets/screens/escape.svg", ["arrive"])
    if choice == "arrive":
        st.session_state.show_escape = False
        st.rerun()


PRACTICE_LOOPS = 4  # clean switches in a row and Needle is ready (each one harder: see art/build.py)
CRAYON_MARKS = 2  # good crayon marks (one on each copy) and he sees the break


def show_crayon(p):
    """The crayon minigame (Grandmaster Flash's secret): both turntables, the break playing on one.
    MARK right when the break is over (the picture only counts it then: mark_hit; else mark_miss):
    Needle's hand stops the record (the beat stops: the page pauses it right then), draws a crayon
    mark where the break starts, and lets it go (mark_done: the beat goes on, on the other copy).
    CRAYON_MARKS good marks, one on each copy, and he sees the break: on to keeping it going.
    STOP leaves without practicing."""
    marking = p["last"] == "marking"
    show = [f"marks-{p['marks']}"] + ([p["last"]] if p["last"] else [])
    enabled = ["mark_done", "stop_practice"] if marking else ["mark_hit", "mark_miss", "stop_practice"]
    choice = svg_screen("crayon", "assets/screens/crayon.svg", enabled, show,
                        audio=st.session_state.get("audio"), nonce=p["nonce"])
    if choice not in enabled:
        return
    if choice == "stop_practice":
        st.session_state.practicing = None
        play_song(None)
    elif choice == "mark_hit":  # his hand stops the record: the beat stops while he marks it
        p.update(marks=p["marks"] + 1, last="marking", nonce=p["nonce"] + 1)
        play_song("think_about_it_break", cmd="pause")
    elif choice == "mark_done":  # he lets it go: the beat goes on
        play_song("think_about_it_break", cmd="resume")
        if p["marks"] >= CRAYON_MARKS:
            p.update(phase="game", last=None)  # he sees the break now: keep it going
        else:
            p.update(last=None, nonce=p["nonce"] + 1)
    else:
        p.update(last="not-there", nonce=p["nonce"] + 1)
    st.rerun()


def show_practice(p):
    """The practice minigame (keep the break going): the break plays on one deck; SPIN BACK the
    other one right before it runs out (the picture only counts it then: loop_hit; too early, or
    too late: loop_miss). PRACTICE_LOOPS clean loops in a row and he has practiced (saved);
    STOP leaves without it."""
    show = [f"deck-{p['deck']}", f"streak-{p['streak']}"] + ([p["last"]] if p["last"] else [])
    enabled = ["loop_hit", "loop_miss", "stop_practice"]
    choice = svg_screen("practice", "assets/screens/practice.svg", enabled, show,
                        audio=st.session_state.get("audio"), nonce=p["nonce"])
    if choice not in enabled:
        return
    if choice == "stop_practice":
        st.session_state.practicing = None
        play_song(None)
    elif choice == "loop_hit":
        p.update(streak=p["streak"] + 1, deck=3 - p["deck"], last="clean", nonce=p["nonce"] + 1)
        if p["streak"] >= PRACTICE_LOOPS:
            st.session_state.practicing = None
            play_song(None, cmd="fade")  # the drum break fades out
            do_action("practice")  # now he has practiced: saved, and the basement says so
    else:  # loop_miss: the break died, from the top
        p.update(streak=0, last="break-died", nonce=p["nonce"] + 1)
    st.rerun()


def start_cypher_move(b, move):
    """Reekz goes into a move: its clip starts from the pose he is in now."""
    b["file"], b["base"] = logic.cypher_clip(b["base"], move), logic.next_base(move)
    b.update(phase="moving", moves=b["moves"] + [move], nonce=b["nonce"] + 1, queued=None)


def show_cypher_battle():
    """The cypher battle (only for show, nothing is saved). Each round Kid Cyclone goes first
    (rival), then the player picks Reekz's moves one by one (choose, moving) until his set is
    over, then the crowd judges (judge); two rounds win the cypher. A move's clip starts from
    the pose Reekz is in (logic.cypher_clip), so his moves connect."""
    b = st.session_state.cypher_battle
    show = [f"round-{b['round']}"] + [f"did-{i}-{m}" for i, m in enumerate(b["moves"])]
    result = logic.cypher_result(b["results"])
    if b["phase"] == "rival":
        enabled = ["reekz_turn"]
    elif b["phase"] == "choose":
        enabled, show = [f"move:{m}" for m in logic.CYPHER_MOVES], show + ["choose"]
    elif b["phase"] == "moving":
        # the next move can be picked while he still does this one (unless this one ends the set)
        enabled = ["move_done"]
        if not logic.set_is_over(b["moves"]):
            enabled += [f"move:{m}" for m in logic.CYPHER_MOVES]
            show += ["choose"] + ([f"queued-{b['queued']}"] if b.get("queued") else [])
    else:  # judge
        reekz, rival = b["results"][-1]
        show += (["judge", "round-won" if reekz > rival else "round-lost", f"reekz-score-{reekz}", f"rival-score-{rival}"]
                 + [f"note-{n}" for n in b["notes"]] + ([f"cypher-{result}"] if result else ["can-next"]))
        enabled = [] if result else ["next_round"]
    enabled += ["leave_cypher"]
    choice = svg_screen("cypher", b["file"], enabled, show, audio=st.session_state.get("audio"), nonce=b["nonce"])
    if choice not in enabled:
        return
    if choice == "leave_cypher":
        st.session_state.in_cypher = False
        play_song(None)  # back to the block: the music stops
    elif choice == "reekz_turn":
        b.update(phase="choose", base="stand", moves=[])
    elif choice.startswith("move:") and b["phase"] == "moving":  # up next, once this move is over
        b["queued"] = choice.split(":", 1)[1]
    elif choice.startswith("move:"):
        start_cypher_move(b, choice.split(":", 1)[1])
    elif choice == "move_done":
        if b.get("queued"):  # straight on into the next move, from the pose this one ended in
            start_cypher_move(b, b.pop("queued"))
        elif logic.set_is_over(b["moves"]):
            reekz, b["notes"] = logic.score_set(b["moves"], b["earlier"])
            rival, _ = logic.score_set(logic.RIVAL_SETS[b["round"] - 1], b["rival_earlier"])
            b.update(phase="judge", results=b["results"] + [(reekz, rival)])
            if logic.cypher_result(b["results"]) == "won":
                do_action("win_cypher")  # the crowd's hat goes round: $10 for the crew, saved
        else:
            b["phase"] = "choose"
    elif choice == "next_round":
        b.update(earlier=b["earlier"] + b["moves"], rival_earlier=b["rival_earlier"] + logic.RIVAL_SETS[b["round"] - 1],
                 round=b["round"] + 1, moves=[], phase="rival", nonce=b["nonce"] + 1)
        b["file"] = f"assets/cypher/rival_{b['round']}.svg"
    st.rerun()


def play_song(song, cmd=None, end=None):
    """Start a song in the browser (each call gets a new id, so PLAY again starts it again).
    song=None stops whatever is playing. cmd="pause" / "resume" pauses the current song or
    goes on from where it was paused, cmd="fade" fades it out. end: the click the page makes
    when the song is over."""
    previous = st.session_state.get("audio")
    src = previous["src"] if cmd and previous else (f"app/static/{logic.SONGS[song]['file']}" if song else None)
    loop = bool(song and logic.SONGS[song].get("loop"))  # e.g. the drum break Needle practices to
    st.session_state.audio = {"src": src, "id": (previous["id"] + 1) if previous else 1, "cmd": cmd, "end": end, "loop": loop}


def start_rapping(rappers):
    """The rappers take the mic one after the other; the next one when the page says a verse is over.
    A rapper whose recording isn't there (yet) is left out."""
    st.session_state.rapping = [r for r in rappers if (APP_DIR / "static" / logic.SONGS[logic.RAPPERS[r]]["file"]).is_file()]
    if st.session_state.rapping:
        play_song(logic.RAPPERS[st.session_state.rapping[0]], end="verse_over")


def stop_rapping():
    if st.session_state.get("rapping"):
        play_song(None)
    st.session_state.rapping = []


def walk_voice(walk, game):
    """What's said during a walk (logic.WALK_LINES), if it's recorded: a voice that waits until
    its bubble shows (static/audio/voices/walks/<walk>/<number>_<speaker>.mp3). One line per walk.
    Some walks' lines need an item (logic.WALK_LINES_WHEN_HAS, e.g. the crayons)."""
    name = Path(walk).stem
    if logic.WALK_LINES_WHEN_HAS.get(name, None) not in (None, *game.inventory):
        return None
    for line, (speaker, _, secs) in enumerate(logic.WALK_LINES.get(name, [])):
        path = APP_DIR / "static" / "audio" / "voices" / "walks" / name / f"{line:02d}_{speaker}.mp3"
        if path.is_file():
            return {"src": f"app/static/audio/voices/walks/{name}/{path.name}",
                    "id": f"walk:{name}:{line}:{st.session_state.get('arrivals', 0)}", "delay": secs}
    return None


def voice_file(scene_id, line, speaker, kind="talk"):
    """The recording of a line of dialogue, if there is one:
    static/audio/voices/<scene>/<number>_<speaker>.mp3 (number = the line's place, from 00);
    the lines for coming back ("back") are in static/audio/voices/<scene>/back/."""
    folder = scene_id if kind == "talk" else f"{scene_id}/{kind}"
    path = APP_DIR / "static" / "audio" / "voices" / folder / f"{line:02d}_{speaker}.mp3"
    return f"app/static/audio/voices/{folder}/{path.name}" if path.is_file() else None


def items_shown(game):
    """Which version of things to show: "has-<item>" for what the crew carries and
    "lacks-<item>" for what it doesn't (e.g. Bible with or without his rhyme book)."""
    return ([f"has-{item}" for item in game.inventory]
            + [f"lacks-{item}" for item in logic.ITEMS if item not in game.inventory])


ITEM_ICONS = {
    "rhyme_book": "📓",
    "service_key": "🗝️",
    "vinyl": "💿",
    "crayons": "🖍️",
    "chips": "🥔",
    "soda": "🥤",
    "candy": "🍬",
}


def backpack(game):
    """What the 🎒 button opens: the items the crew carries (in the order picked up) and its cash."""
    return {"items": [{"id": item, "name": logic.ITEMS[item], "icon": ITEM_ICONS.get(item, "❔")}
                      for item in game.inventory],
            "cash": f"${game.money / 100:.2f}"}


def show_ending(game):
    """The ending (PT05): clearly named, can be looked at again (RESUME), and the way back to
    the start, where START asks before the old game is replaced. After a lost rap battle it's
    game over: RESTART starts a new game straight away, from the story intro."""
    if game.ending == "ending_lost_battle":
        if svg_screen("ending", f"assets/endings/{game.ending}.svg", ["restart"], show=["lost-choked"]) == "restart":
            start_new_game()
            st.rerun()
        return
    if svg_screen("ending", f"assets/endings/{game.ending}.svg", ["to_start"]) == "to_start":
        del st.session_state["game"]
        st.session_state.walk = None
        st.rerun()


def show_scene_picture(game, scene):
    """The scene picture with everything the player can click in it.

    Clicks: an action id (a way out or taking an item, through the game rules), "next" (the
    next line of the conversation), "inspect:<thing>" (open the sign about a thing), "close"
    (close it), "dismiss" (put away the message about what just happened).
    Looking at things and talking are not moves: nothing is saved.

    The picture shows "offer-<action>" for every item still there to take, "has-<item>" for
    every item the crew carries, "done-<action>" right after an action with a message and
    "rejected-<action>" right after an action the rules turned down (both until the next click).
    """
    talk = st.session_state.setdefault("talk", {})
    # "talk" the first time, "back" coming back, "after" right after being turned down (see logic)
    kind, lines = logic.conversation(game, tried=st.session_state.get("tried_before"),
                                     came_from=st.session_state.get("came_from"),
                                     just_did=st.session_state.get("just_did"))
    key = game.current_scene if kind == "talk" else f"{game.current_scene}:{kind}"
    line = talk.setdefault(key, 0)
    done = st.session_state.get("last_done")
    rejected = st.session_state.get("last_rejected")
    turned_down = logic.said_when_turned_down(game, rejected) if rejected else []
    if turned_down:  # e.g. Reekz at the chained gate: his bubble shows with the sign, until the next click
        kind, lines, key, line = "locked", turned_down, None, 0
    looking_at = st.session_state.get("looking_at")
    talking = [f"{kind}-{line}"] if line < len(lines) else []
    actions = logic.available_actions(game)
    items = [f"offer-{a['id']}" for a in actions if "collects" in a]
    just_done = ([f"done-{done}"] if done else []) + ([f"rejected-{rejected}"] if rejected else [])
    carried = (items_shown(game) + [f"battle-{game.rap_battle or 'open'}"] + (["practiced"] if game.practiced else [])
               + (["stuck"] if game.stuck else []) + (["met-flash"] if game.met_flash else []))
    picking = st.session_state.get("picking")
    rapping = st.session_state.get("rapping")
    practicing = st.session_state.get("practicing")
    if practicing and practicing.get("phase") == "trying":
        # his first try behind the decks: the break, always off; the picture says when it's over
        enabled, show = ["tried"], items + carried + ["practicing", "needle-busy", "trying"]
    elif practicing:
        # Needle takes the record behind the decks; the picture says when he's ready (the minigame)
        enabled, show = ["decks_ready"], items + carried + ["practicing", "needle-busy"]
    elif rapping:
        # someone is on the mic: SKIP, the next verse when this one is over, or leave the station
        enabled = ["skip_verse", "verse_over"] + [a["id"] for a in actions if "target" in a]
        # the crowd cheers for a verse and boos Bible off when he chokes; whoever raps isn't in his spot
        who = rapping[0]
        crowd = "booing" if who == "bible_chokes" else "cheering"
        show = items + carried + just_done + ["rapping", f"rapping-{who}", f"mic-{who.split('_')[0]}", crowd]
    elif picking:
        # Needle walks over, picks the record up and puts it on; the picture says when he's done
        enabled, show = [f"play_record:{picking}"], items + carried + ["needle-busy", f"pick-{picking}"]
    elif looking_at:
        # the sign can offer to take the thing (e.g. the rhyme book), while it's still there
        thing = scene.get("things", {}).get(looking_at, {})
        take = thing.get("take")
        takeable = [take] if take and take in [a["id"] for a in actions] else []
        playable = [f"play:{thing['song']}"] if thing.get("song") else []
        readable = [f"read:{looking_at}"] if thing.get("read") else []
        shootable = [f"shoot:{shot}" for shot in thing.get("shots", {})]
        joinable = [f"join:{looking_at}"] if thing.get("join") else []
        enabled = ["close"] + takeable + playable + readable + shootable + joinable
        show = [f"inspect-{looking_at}"] + talking + items + carried
    else:
        enabled = ([a["id"] for a in actions if not a.get("by_app")]  # (by_app: the app gives it, e.g. the cypher's prize)
                   + (["next"] if talking else [])
                   + [f"inspect:{thing}" for thing, info in scene.get("things", {}).items()
                      if info.get("unless") not in game.inventory
                      and (not info.get("when_flag") or getattr(game, info["when_flag"]))]  # e.g. the cypher, after Flash
                   + [f"pick:{record}" for record in scene.get("records", [])
                      if logic.RECORDS[record].get("requires") in (None, *game.inventory)]
                   + (["dismiss"] if just_done else []))
        show = talking + items + carried + just_done
        shot = st.session_state.get("shooting")
        if shot:  # a shot on the court: Needle dunks; Bible takes the three, unless he carries his book
            who = "needle" if shot == "dunk" or "rhyme_book" in game.inventory else "bible"
            show += ["shooting", f"shot-{shot}-{who}", f"{who}-shooting"] + (["bible-shooting"] if shot == "dunk" else [])  # Bible passes
            enabled += ["shot_done"]
    # the scene's background sound, except while Needle puts a record on or tries the break (it fades out)
    ambience = None if picking or (practicing and practicing.get("phase") == "trying") else scene.get("ambience")
    # the speaker's voice for the line in the bubble (each line is spoken once, when it comes up)
    voice = None
    if talking and not picking:
        src = voice_file(game.current_scene, line, lines[line][0], kind)
        # (coming back plays again on every arrival: a new id each time, or the page wouldn't speak it again)
        arrival = f":{st.session_state.get('arrivals', 0)}" if kind != "talk" else ""
        if kind == "locked":  # each time it's turned down
            arrival = f":{st.session_state.get('turned_down', 0)}"
        voice = {"src": src, "id": f"{game.current_scene}:{kind}:{line}{arrival}"} if src else None
    choice = svg_screen("picture", scene_file(game.current_scene), enabled, show, audio=st.session_state.get("audio"),
                        ambience=ambience, voice=voice, backpack=backpack(game))
    if choice not in enabled:
        return
    if choice in ("skip_verse", "verse_over"):  # the outcome comes up when the rapping is over
        if choice == "skip_verse":
            stop_rapping()
        else:
            st.session_state.rapping = rapping[1:]
            if st.session_state.rapping:
                play_song(logic.RAPPERS[st.session_state.rapping[0]], end="verse_over")
        st.rerun()
    st.session_state.last_done = None  # any click puts the message away
    st.session_state.last_rejected = None
    st.session_state.shooting = None  # ... and ends a shot on the court
    if choice == "dismiss":
        pass
    elif choice == "next" and key:  # (a turned-down line just goes away with the click)
        talk[key] = line + 1
    elif choice == "next":
        pass
    elif choice.startswith("pick:"):  # Needle goes to get the record (only for show, nothing is saved)
        st.session_state.picking = choice.split(":", 1)[1]
    elif choice.startswith("play_record:"):  # it's on the turntable: show it from above
        st.session_state.picking = None
        st.session_state.spinning = choice.split(":", 1)[1]
        st.session_state.record_paused = False
        song = logic.RECORDS[st.session_state.spinning]["song"]
        if song:
            play_song(song)
    elif choice.startswith("read:"):  # READ IT: open the rhyme book (only for show, nothing is saved)
        st.session_state.looking_at = None
        st.session_state.reading = 1
    elif choice == "practice" and "crayons" not in game.inventory:
        do_action("practice")  # turned down: Flash said the secret lies in the crayon
    elif choice == "practice":  # PRACTICE THE BREAK: behind the decks first, then the minigames decide
        st.session_state.practicing = {"phase": "walk", "marks": 0, "deck": 1, "streak": 0, "last": None, "nonce": 0}
    elif choice == "try_practice":  # his turntables: he tries the break first (only for show), then the rule
        st.session_state.practicing = {"phase": "walk", "trying": True}
    elif choice == "decks_ready" and practicing.get("trying"):
        practicing["phase"] = "trying"
        play_song("think_about_it_off")  # he tries to loop the break: it's always off
    elif choice == "tried":
        st.session_state.practicing = None
        play_song(None, cmd="fade")
        do_action("try_practice")  # now he's stuck: saved, and the crew talks about Flash
    elif choice == "decks_ready":
        st.session_state.practicing["phase"] = "mark"  # first he marks the break with the crayon
        play_song("think_about_it_break")  # he practices to the drum break, on a loop
    elif choice.startswith("shoot:"):  # DUNK / 3-POINTER on the ball's sign (only for show, nothing is saved)
        st.session_state.looking_at = None
        st.session_state.shooting = choice.split(":", 1)[1]
    elif choice == "shot_done":
        pass
    elif choice.startswith("join:"):  # JOIN IN on the cypher: the battle, to Apache (only for show)
        st.session_state.looking_at = None
        st.session_state.in_cypher = True
        st.session_state.cypher_battle = {"round": 1, "phase": "rival", "file": "assets/cypher/rival_1.svg", "nonce": 0,
                                          "base": "stand", "moves": [], "earlier": [], "rival_earlier": [],
                                          "results": [], "notes": []}
        play_song("apache")
    elif choice.startswith("play:"):  # PLAY on a sign: the sign stays open
        play_song(choice.split(":", 1)[1])
    elif choice == "close":
        st.session_state.looking_at = None
    elif looking_at:  # TAKE IT on the sign
        st.session_state.looking_at = None
        do_action(choice)
    elif choice.startswith("inspect:"):
        st.session_state.looking_at = choice.split(":", 1)[1]
    else:
        do_action(choice)
    st.rerun()


def show_game():
    game = st.session_state.game
    scene = logic.SCENES[game.current_scene]

    # MC Bible's rhyme book, open: his view of the pages, which the player can turn
    reading = st.session_state.get("reading")
    if reading:
        spreads = 2
        enabled = (["page_next"] if reading < spreads else []) + (["page_prev"] if reading > 1 else []) + ["close_book"]
        choice = svg_screen("rhymebook", f"assets/screens/rhymebook_{reading}.svg", enabled,
                            ambience=scene.get("ambience"))
        if choice == "page_next":
            st.session_state.reading = reading + 1
        elif choice == "page_prev":
            st.session_state.reading = reading - 1
        elif choice == "close_book":
            st.session_state.reading = None
        if choice in enabled:
            st.rerun()
        return

    # Needle practices the break: keep it going, from deck to deck
    practice = st.session_state.get("practicing")
    if practice and practice["phase"] == "mark":
        show_crayon(practice)
        return
    if practice and practice["phase"] == "game":
        show_practice(practice)
        return

    # The b-boy cypher in front of the corner store: Reekz battles Kid Cyclone
    if st.session_state.get("in_cypher"):
        show_cypher_battle()
        return

    # A record on the turntable, seen from above
    spinning = st.session_state.get("spinning")
    if spinning:
        paused = st.session_state.get("record_paused", False)
        choice = svg_screen("turntable", f"assets/records/{spinning}.svg", ["back", "toggle_play"],
                            show=["paused"] if paused else [], audio=st.session_state.get("audio"))
        if choice == "back":
            st.session_state.spinning = None
            st.session_state.record_paused = False
            play_song(None)  # the record comes off: the music stops
            st.rerun()
        elif choice == "toggle_play":  # START / STOP on the turntable
            st.session_state.record_paused = not paused
            play_song(None, cmd="pause" if not paused else "resume")
            st.rerun()
        return

    # Arriving by walking shows the walk (drawn inline: st.image would not animate it). It ends
    # at the door of the next place: ENTER leads in.
    walk = st.session_state.get("walk")
    if walk:
        if svg_screen("picture", walk, enabled=["enter"], show=items_shown(game), ambience="street_ambience",
                      voice=walk_voice(walk, game), backpack=backpack(game)) == "enter":  # the street
            st.session_state.walk = None
            st.rerun()
        if scene_file(game.current_scene):
            return

    # A scene with its own picture is played inside the picture: its ways out are graffiti
    # buttons, its conversation goes on with each click, its things can be clicked. Nothing
    # is shown under it.
    elif scene_file(game.current_scene):
        show_scene_picture(game, scene)
        return

    st.header(scene["title"])
    st.write(scene["text"])

    feedback = st.session_state.get("feedback")
    if feedback and feedback[1]:
        accepted, message = feedback
        (st.success if accepted else st.warning)(message)

    for action in logic.available_actions(game):
        st.button(action["label"], key=action["id"], on_click=do_action, args=(action["id"],))


if "game" not in st.session_state:
    show_menu()
elif st.session_state.get("show_intro"):
    show_intro()
elif st.session_state.get("show_escape"):
    show_escape()
elif st.session_state.game.ending and not st.session_state.get("rapping"):  # (a lost battle: after the rapping)
    show_ending(st.session_state.game)
else:
    show_game()
