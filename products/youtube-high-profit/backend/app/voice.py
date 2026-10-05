from pathlib import Path
import wave, struct

def make_silence(output: str, seconds: int, sample_rate: int = 16000):
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    frames=sample_rate*max(1,seconds)
    with wave.open(str(path),"w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sample_rate)
        w.writeframes(struct.pack("<h",0)*frames)
    return str(path)
