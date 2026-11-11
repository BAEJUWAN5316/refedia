import { useEffect, useRef, useState } from 'react';
import { API_URL } from '../config';

let apiPromise;
function loadAPI() {
    if (window.YT?.Player) return Promise.resolve(window.YT);
    if (!apiPromise) apiPromise = new Promise((resolve, reject) => {
        const previous = window.onYouTubeIframeAPIReady;
        window.onYouTubeIframeAPIReady = () => { previous?.(); resolve(window.YT); };
        const script = document.createElement('script');
        script.src = 'https://www.youtube.com/iframe_api';
        script.onerror = () => { apiPromise = null; reject(new Error('플레이어를 불러오지 못했습니다.')); };
        document.head.appendChild(script);
    });
    return apiPromise;
}
function videoId(url) {
    try {
        const parsed = new URL(url);
        const host = parsed.hostname.replace(/^www\./, '');
        if (host === 'youtu.be') return parsed.pathname.slice(1).split('/')[0];
        if (['youtube.com', 'm.youtube.com', 'youtube-nocookie.com'].includes(host))
            return parsed.searchParams.get('v') || parsed.pathname.split('/')[2] || '';
    } catch { /* Invalid URL */ }
    return '';
}
const clock = value => `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, '0')}`;

export default function YouTubePlayer({ url, preview = false }) {
    const mount = useRef(null);
    const player = useRef(null);
    const [time, setTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [ready, setReady] = useState(false);
    const [message, setMessage] = useState('');
    const [copying, setCopying] = useState(false);
    useEffect(() => {
        let disposed = false;
        let timer;
        const target = document.createElement('div');
        mount.current.appendChild(target);
        loadAPI().then(YT => {
            if (disposed) return;
            player.current = new YT.Player(target, {
                videoId: videoId(url), width: '100%', height: '100%',
                playerVars: { autoplay: 1, controls: preview ? 0 : 1, playsinline: 1, origin: window.location.origin },
                events: {
                    onReady: event => {
                        if (preview) event.target.mute();
                        event.target.playVideo();
                        setReady(true);
                        timer = setInterval(() => {
                            setTime(event.target.getCurrentTime() || 0);
                            setDuration(event.target.getDuration() || 0);
                        }, 250);
                    },
                    onError: () => setMessage('이 영상은 여기서 재생할 수 없습니다. YouTube에서 확인해주세요.'),
                },
            });
        }).catch(error => { if (!disposed) setMessage(error.message); });
        return () => { disposed = true; clearInterval(timer); player.current?.destroy(); player.current = null; target.remove(); };
    }, [url, preview]);
    const copyFrame = async () => {
        if (!navigator.clipboard?.write || !window.ClipboardItem) {
            setMessage('프레임 복사는 HTTPS의 Chrome 또는 Edge에서 이용해주세요.'); return;
        }
        player.current?.pauseVideo();
        const timestamp = player.current?.getCurrentTime() || 0;
        setCopying(true); setMessage('');
        try {
            const image = fetch(`${API_URL}/api/youtube/frame?${new URLSearchParams({ url, seconds: timestamp })}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            }).then(async response => {
                if (!response.ok) throw new Error('프레임을 추출하지 못했습니다. 잠시 후 다시 시도해주세요.');
                return response.blob();
            });
            await navigator.clipboard.write([new ClipboardItem({ 'image/png': image })]);
            setMessage(`${clock(timestamp)} 프레임을 복사했습니다.`);
        } catch (error) { setMessage(error.message); }
        finally { setCopying(false); }
    };
    return <div className={`youtube-player ${preview ? 'is-preview' : ''}`}>
        <div ref={mount} className="youtube-mount" />
        <div className="video-timeline" onClick={event => { event.preventDefault(); event.stopPropagation(); }}>
            <span>{clock(time)}</span>
            <input aria-label="영상 재생 위치" type="range" min="0" max={duration || 1} step="0.1" value={Math.min(time, duration || 1)} disabled={!ready || !duration}
                onChange={event => { const next = Number(event.target.value); player.current?.seekTo(next, true); setTime(next); }} />
            <span>{clock(duration)}</span>
            {!preview && <button className="btn btn-secondary" disabled={!ready || copying} onClick={copyFrame}>{copying ? '추출 중…' : '현재 프레임 복사'}</button>}
        </div>
        {message && <p className="player-message" role="status">{message}</p>}
    </div>;
}
