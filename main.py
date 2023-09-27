import sys
import os
import time
from threading import Thread
from typing import Dict, Any, Optional, Sequence
from googletrans import Translator
import pvleopard
import pysrt
from moviepy.editor import *
import audio_to_subtitle_converter as atsc
import srt_writer_reader as swr
from deep_translator import GoogleTranslator
import sys
from gtts import gTTS
print('Press 1  enter video link \n Press 2  enter audio link \n Press 3  enter video link subtitled with french  voice ')
n=input()

if int(n)==1:

    print('Enter video link')
    vi = input()

    class ProgressAnimation(Thread):
        def __init__(self, prefix: str, step_sec: float = 0.19) -> None:
            super().__init__()

            self._prefix = prefix
            self._step_sec = step_sec
            self._frames = (
                ".  ",
                ".. ",
                "...",
                " ..",
                "  .",
                "   "
            )
            self._stop = False

        def run(self) -> None:
            while True:
                for frame in self._frames:
                    if self._stop:
                        sys.stdout.write('\r%s\r' % (" " * (len(self._prefix) + 1 + len(frame))))
                        self._stop = False
                        return
                    sys.stdout.write('\r%s %s' % (self._prefix, frame))
                    sys.stdout.flush()
                    time.sleep(self._step_sec)

        def stop(self) -> None:
            self._stop = True
            while self._stop:
                pass


    def second_to_timecode(x: float) -> str:
        hour, x = divmod(x, 3600)
        minute, x = divmod(x, 60)
        second, x = divmod(x, 1)
        millisecond = int(x * 1000.)

        return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)


    def to_srt(words: Sequence[pvleopard.Leopard.Word], endpoint_sec: float = 1.,
               length_limit: Optional[int] = 16) -> str:
        def _helper(end: int) -> None:
            lines.append("%d" % section)
            lines.append(
                "%s --> %s" %
                (second_to_timecode(words[start].start_sec), second_to_timecode(words[end].end_sec)))
            lines.append(' '.join(x.word for x in words[start:(end + 1)]))
            lines.append('')

        lines = list()
        section = 0
        start = 0
        for k in range(1, len(words)):
            if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                    (length_limit is not None and (k - start) >= length_limit):
                _helper(k - 1)
                start = k
                section += 1
        _helper(len(words) - 1)

        return '\n'.join(lines)


    def main() -> None:
        access_key = 'Y/AcTvD1e1Ha79bKiLkEab+B0Tl14AGIWAaCrq5NxHDP+Jx+z1CjgQ=='  # Replace with your actual Picovoice Access Key
        video_path = str(vi)  # Replace with the path to your local video file
        output_subtitle_path = 'subtitles.srt'  # Replace with the path where you want to save the subtitle
        model_path = ''  # Optionally specify the model path if needed

        anime = ProgressAnimation('Initializing Leopard with AccessKey `%s`' % access_key)
        anime.start()
        try:
            leopard = pvleopard.create(access_key=access_key)
        except pvleopard.LeopardError as e:
            print("Failed to initialize Leopard with `%s`" % e)
            exit(1)
        finally:
            anime.stop()

        if not os.path.exists(video_path):
            print("`%s` does not exist" % video_path)
            exit(1)

        anime = ProgressAnimation('Transcribing `%s`' % video_path)
        anime.start()
        try:
            transcript, words = leopard.process_file(video_path)
        except pvleopard.LeopardError as e:
            print("Failed to transcribe audio with `%s`" % e)
            exit(1)
        finally:
            anime.stop()

        with open(output_subtitle_path, 'w') as f:
            f.write(to_srt(words))
            f.write('\n')
        print('Saved transcription into `%s`' % output_subtitle_path)


    def translate_srt(input_srt_path, output_srt_path, target_language='en'):
        # Initialize the translator

        print('Translating text....')

        # Load the input SRT file
        subs = pysrt.open(input_srt_path)

        # Create an empty SRT object to store the translated subtitles
        translated_subs = pysrt.SubRipFile()

        # Translate each subtitle and add it to the translated_subs object
        for sub in subs:
            try:
                # Translate the subtitle text to the target language
                translated = GoogleTranslator(source='auto', target='fr').translate(sub.text)
                print(translated)
                # Create a new subtitle entry with the translated text
                translated_sub = pysrt.SubRipItem(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    text=translated
                )

                # Append the translated subtitle to the result
                translated_subs.append(translated_sub)
            except:
                print()
        # Save the translated subtitles to the output SRT file
        translated_subs.save(output_srt_path, encoding='utf-8')


    def time_to_seconds(time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


    def create_subtitle_clips(subtitles, videosize, fontsize=20, font='Arial', color='yellow', debug=False):
        subtitle_clips = []

        for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)
            duration = end_time - start_time

            video_width, video_height = videosize

            text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color='black',
                                 size=(video_width * 3 / 4, None), method='caption').set_start(start_time).set_duration(
                duration)
            subtitle_x_position = 'center'
            subtitle_y_position = video_height * 4 / 5

            text_position = (subtitle_x_position, subtitle_y_position)
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips


    if __name__ == '__main__':

        main()
        try:
            input_srt_file = r'subtitles.srt'  # Replace with the path to your input SRT file
            output_srt_file = r'output_subtitles.srt'  # Replace with the desired output SRT file path

            translate_srt(input_srt_file, output_srt_file)

            print("SRT file translation complete.")
            srtfilename = 'output_subtitles.srt'
            mp4filename = 'self.lineEdit_2.text()'
            video = VideoFileClip(mp4filename)
            subtitles = pysrt.open(srtfilename)

            output_video_file = 'finalvideo.mp4'

            print("Output file name: ", output_video_file)

            # Create subtitle clips
            subtitle_clips = create_subtitle_clips(subtitles, video.size)

            # Add subtitles to the video
            final_video = CompositeVideoClip([video] + subtitle_clips)

            # Write output video file
            final_video.write_videofile(output_video_file)
        except Exception as e:
            print(e)

elif int(n)==2:
    print('Enter audio link')
    vi = input()

    def AudioToSRTOnSameLang(audio_file_name, audio_language, file_name):

        srt_content = atsc.get_large_audio_transcription(audio_file_name, audio_language)
        swr.writeSRTFile(file_name, srt_content, True)


    AudioToSRTOnSameLang(vi, 'en', 'english_subtitles')


    def translate_srt(input_srt_path, output_srt_path, target_language='fr'):
        # Initialize the translator
        translator = Translator()

        # Load the input SRT file
        subs = pysrt.open(input_srt_path)

        # Create an empty SRT object to store the translated subtitles
        translated_subs = pysrt.SubRipFile()

        # Translate each subtitle and add it to the translated_subs object
        for sub in subs:
            # Translate the subtitle text to the target language
            translated_text = translator.translate(sub.text, dest=target_language).text

            # Create a new subtitle entry with the translated text
            translated_sub = pysrt.SubRipItem(
                index=sub.index,
                start=sub.start,
                end=sub.end,
                text=translated_text
            )

            # Append the translated subtitle to the result
            translated_subs.append(translated_sub)

        # Save the translated subtitles to the output SRT file
        translated_subs.save(output_srt_path, encoding='utf-8')


    input_srt_file = r'english_subtitles.srt'  # Replace with the path to your input SRT file
    output_srt_file = '\french_subtitles.srt'  # Replace with the desired output SRT file path

    translate_srt(input_srt_file, output_srt_file)

    print("SRT file translation complete.")
elif int(n)==3:
    print('Enter video link')
    vi = input()


    class ProgressAnimation(Thread):
        def __init__(self, prefix: str, step_sec: float = 0.19) -> None:
            super().__init__()

            self._prefix = prefix
            self._step_sec = step_sec
            self._frames = (
                ".  ",
                ".. ",
                "...",
                " ..",
                "  .",
                "   "
            )
            self._stop = False

        def run(self) -> None:
            while True:
                for frame in self._frames:
                    if self._stop:
                        sys.stdout.write('\r%s\r' % (" " * (len(self._prefix) + 1 + len(frame))))
                        self._stop = False
                        return
                    sys.stdout.write('\r%s %s' % (self._prefix, frame))
                    sys.stdout.flush()
                    time.sleep(self._step_sec)

        def stop(self) -> None:
            self._stop = True
            while self._stop:
                pass


    def second_to_timecode(x: float) -> str:
        hour, x = divmod(x, 3600)
        minute, x = divmod(x, 60)
        second, x = divmod(x, 1)
        millisecond = int(x * 1000.)

        return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)


    def to_srt(words: Sequence[pvleopard.Leopard.Word], endpoint_sec: float = 1.,
               length_limit: Optional[int] = 16) -> str:
        def _helper(end: int) -> None:
            lines.append("%d" % section)
            lines.append(
                "%s --> %s" %
                (second_to_timecode(words[start].start_sec), second_to_timecode(words[end].end_sec)))
            lines.append(' '.join(x.word for x in words[start:(end + 1)]))
            lines.append('')

        lines = list()
        section = 0
        start = 0
        for k in range(1, len(words)):
            if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                    (length_limit is not None and (k - start) >= length_limit):
                _helper(k - 1)
                start = k
                section += 1
        _helper(len(words) - 1)

        return '\n'.join(lines)


    def main() -> None:
        access_key = 'Y/AcTvD1e1Ha79bKiLkEab+B0Tl14AGIWAaCrq5NxHDP+Jx+z1CjgQ=='  # Replace with your actual Picovoice Access Key
        video_path = str(vi)  # Replace with the path to your local video file
        output_subtitle_path = 'subtitles.srt'  # Replace with the path where you want to save the subtitle
        model_path = ''  # Optionally specify the model path if needed

        anime = ProgressAnimation('Initializing Leopard with AccessKey `%s`' % access_key)
        anime.start()
        try:
            leopard = pvleopard.create(access_key=access_key)
        except pvleopard.LeopardError as e:
            print("Failed to initialize Leopard with `%s`" % e)
            exit(1)
        finally:
            anime.stop()

        if not os.path.exists(video_path):
            print("`%s` does not exist" % video_path)
            exit(1)

        anime = ProgressAnimation('Transcribing `%s`' % video_path)
        anime.start()
        try:
            transcript, words = leopard.process_file(video_path)
        except pvleopard.LeopardError as e:
            print("Failed to transcribe audio with `%s`" % e)
            exit(1)
        finally:
            anime.stop()

        with open(output_subtitle_path, 'w') as f:
            f.write(to_srt(words))
            f.write('\n')
        print('Saved transcription into `%s`' % output_subtitle_path)


    def translate_srt(input_srt_path, output_srt_path, target_language='en'):
        # Initialize the translator

        print('Translating text....')

        # Load the input SRT file
        subs = pysrt.open(input_srt_path)

        # Create an empty SRT object to store the translated subtitles
        translated_subs = pysrt.SubRipFile()

        # Translate each subtitle and add it to the translated_subs object
        for sub in subs:
            try:
                # Translate the subtitle text to the target language
                translated = GoogleTranslator(source='auto', target='fr').translate(sub.text)
                print(translated)
                # Create a new subtitle entry with the translated text
                translated_sub = pysrt.SubRipItem(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    text=translated
                )

                # Append the translated subtitle to the result
                translated_subs.append(translated_sub)
            except:
                print()
        # Save the translated subtitles to the output SRT file
        translated_subs.save(output_srt_path, encoding='utf-8')


    def time_to_seconds(time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


    def create_subtitle_clips(subtitles, videosize, fontsize=20, font='Arial', color='yellow', debug=False):
        subtitle_clips = []

        for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)
            duration = end_time - start_time

            video_width, video_height = videosize

            text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color='black',
                                 size=(video_width * 3 / 4, None), method='caption').set_start(start_time).set_duration(
                duration)
            subtitle_x_position = 'center'
            subtitle_y_position = video_height * 4 / 5

            text_position = (subtitle_x_position, subtitle_y_position)
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips


    if __name__ == '__main__':

        main()
        try:
            input_srt_file = r'subtitles.srt'  # Replace with the path to your input SRT file
            output_srt_file = r'output_subtitles.srt'  # Replace with the desired output SRT file path

            translate_srt(input_srt_file, output_srt_file)

            print("SRT file translation complete.")
            srtfilename = 'output_subtitles.srt'
            mp4filename = str(vi)
            video = VideoFileClip(mp4filename)
            subtitles = pysrt.open(srtfilename)

            output_video_file = 'finalvideo.mp4'

            print("Output file name: ", output_video_file)

            # Create subtitle clips
            subtitle_clips = create_subtitle_clips(subtitles, video.size)

            # Add subtitles to the video
            final_video = CompositeVideoClip([video] + subtitle_clips)

            # Write output video file
            final_video.write_videofile(output_video_file)
        except Exception as e:
            print(e)

    print('Adding voice')
    input_video_path = r'finalvideo.mp4'

    # Output video file path
    output_video_path = r'muted.mp4'

    # Load the video clip
    video = VideoFileClip(input_video_path)

    # Set the audio of the video to None (muting it)
    video = video.set_audio(None)

    # Write the muted video to the output file
    video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    clips = []

    subtitles = pysrt.open('output_subtitles.srt')
    def time_to_seconds(time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


    for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)


            tts = gTTS(str(subtitle.text))

            tts.save(r'ved.wav')
            audio = AudioFileClip(r'ved.wav')
            videoclips = VideoFileClip(r'muted.mp4').subclip(start_time, end_time)
            videoclip = videoclips.set_audio(audio)
            clips.append(videoclip)


    # Add subtitles to the video
    final_video = concatenate_videoclips(clips)

    # Write output video file
    final_video.write_videofile(r'Finalvoicevideo')







