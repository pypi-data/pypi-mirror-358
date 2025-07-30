import wave


def get_wav_info(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.getframerate(), wav_file.getnchannels()


def read_audio_file(file_path):
    """
    读取音频文件并通过yield返回PCM流

    Args:
        file_path (str): 音频文件路径

    Yields:
        bytes: PCM音频数据块
    """
    with wave.open(file_path, "rb") as wav_file:
        while True:
            pcm = wav_file.readframes(960)  # 每次读取960帧（60ms的音频数据）
            if not pcm:
                break
            yield pcm
