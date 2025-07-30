# PewHits Radio SDK

A lightweight, async Python client SDK for interacting with PewHits Radio's WebSocket-based backend. This library enables applications and bots to fetch, queue, skip, block, and play songs seamlessly, using a request-response WebSocket pattern.

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install pewhits-client-sdk==0.9
```

---

## 🚀 What's New in v0.1

* ✅ **README.md added** — now you know how to use it 😄
* 🎯 Cleaned up and documented all data models
* 🔄 Structured request/response pattern with `rid` support
* 🧠 Strong typing and cleaner logic
* 🧹 Ready for production bots and clients

---

## 🎵 Features

* Get **now playing** song
* See **next coming** song
* View full **queue**
* **Skip** current song
* **Block/Unblock** tracks
* **Remove** songs from queue
* **Play** any Spotify track
* Auto **keepalive** ping support
* Full **radio reload** request

---

## 🧹 Request/Response Models

### 🔁 Standard Requests

| Request Class        | Response Returned     |
| -------------------- | --------------------- |
| `NowPlayingRequest`  | `NowPlayingResponse`  |
| `NextComingRequest`  | `NextComingResponse`  |
| `QueueRequest`       | `QueueResponse`       |
| `BlocklistRequest`   | `BlocklistResponse`   |
| `SkipSongRequest`    | `SkipSongResponse`    |
| `BlockSongRequest`   | `BlockSongResponse`   |
| `UnblockSongRequest` | `UnblockSongResponse` |
| `RemoveSongRequest`  | `RemoveSongResponse`  |
| `PlaySongRequest`    | `PlaySongResponse`    |
| `ReloadAllRequest`   | `ReloadAllResponse`   |
| `KeepaliveRequest`   | `KeepaliveResponse`   |

### 📦 Data Models

* `NowPlayingSong`
* `NextComingSong`
* `QueueSong`
* `BlockedSongs`

These are returned inside each respective `.data` field.

---

## 🧪 Development

Want to run and test locally?

```bash
git clone https://github.com/chitranshsh/pewhits-client-sdk.git
cd pewhits-client-sdk
pip install -e .
```

Or if you're using `poetry`:

```bash
poetry install
poetry run pytest
```

---

## 🤝 Contributing

All improvements are welcome 💡
Feel free to open issues or submit a PR!

---

## 📄 License

License © 2025 Chitransh Shrivastava

---

## 🌐 Links

* **PyPI:** [https://pypi.org/project/pewhits-client-sdk](https://pypi.org/project/pewhits-client-sdk)
* **GitHub:** [https://github.com/chitranshsh/pewhits-client-sdk](https://github.com/chitranshsh/pewhits-client-sdk)

---

## 💖 Author

**Chitransh Shrivastava**
CS B.Tech + Open Source Builder 💻
Find me on [GitHub](https://github.com/chitranshsh)

---

Made with love and music 🎶💫
