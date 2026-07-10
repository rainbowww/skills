package kr.rainbowww.subtitle

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.schabi.newpipe.extractor.NewPipe
import org.schabi.newpipe.extractor.ServiceList

/**
 * 자막 변환기 — 독립 안드로이드 앱(폰만으로 동작 목표).
 *
 * 단계별 개발:
 *  1) 설치되는 진짜 APK + 화면 + 유튜브 주소 인식.  (완료)
 *  2) (현재) NewPipeExtractor 로 폰에서 오디오 스트림 추출.
 *  3) whisper.cpp 온디바이스 한국어 음성 인식 → 자막.
 */
class MainActivity : AppCompatActivity() {

    @Volatile
    private var newPipeReady = false

    private val videoIdPatterns = listOf(
        Regex("(?:v=|/)([\\w-]{11})(?:[?&#]|\$)"),
        Regex("youtu\\.be/([\\w-]{11})"),
        Regex("shorts/([\\w-]{11})"),
        Regex("embed/([\\w-]{11})"),
    )

    private fun parseVideoId(url: String): String? {
        val u = url.trim()
        for (p in videoIdPatterns) {
            val m = p.find(u)
            if (m != null) return m.groupValues[1]
        }
        return null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val urlInput = findViewById<EditText>(R.id.urlInput)
        val convertBtn = findViewById<Button>(R.id.convertBtn)
        val statusText = findViewById<TextView>(R.id.statusText)
        val resultText = findViewById<TextView>(R.id.resultText)

        convertBtn.setOnClickListener {
            val url = urlInput.text.toString().trim()
            val id = parseVideoId(url)
            if (id == null) {
                statusText.text = "유튜브 영상 주소가 아닙니다. URL을 확인해 주세요."
                resultText.visibility = View.GONE
                return@setOnClickListener
            }
            statusText.text = "영상 정보를 가져오는 중... (폰에서 직접)"
            resultText.visibility = View.GONE
            convertBtn.isEnabled = false
            extractAudio(id, statusText, resultText, convertBtn)
        }
    }

    /** 2단계: 폰에서 유튜브 오디오 스트림 정보를 추출한다(백그라운드 스레드). */
    private fun extractAudio(
        videoId: String,
        statusText: TextView,
        resultText: TextView,
        convertBtn: Button,
    ) {
        Thread {
            try {
                if (!newPipeReady) {
                    NewPipe.init(DownloaderImpl.getInstance())
                    newPipeReady = true
                }
                val service = ServiceList.YouTube
                val handler = service.streamLHFactory
                    .fromUrl("https://www.youtube.com/watch?v=$videoId")
                val extractor = service.getStreamExtractor(handler)
                extractor.fetchPage()

                val title = extractor.name ?: "제목 없음"
                val audios = extractor.audioStreams
                val best = audios.maxByOrNull { it.averageBitrate }
                val bitrate = best?.averageBitrate ?: -1
                val fmt = best?.format?.getName() ?: "?"

                runOnUiThread {
                    statusText.text = "오디오 스트림 확인 완료 (폰에서 직접)"
                    resultText.visibility = View.VISIBLE
                    resultText.text = buildString {
                        appendLine("제목: $title")
                        appendLine("오디오 트랙: ${audios.size}개")
                        appendLine("최고 음질: ${if (bitrate > 0) "$bitrate kbps" else "확인됨"} ($fmt)")
                        appendLine()
                        append("다음 단계: 이 오디오를 폰에서 받아 한국어 음성 인식(whisper.cpp)으로 자막을 만듭니다.")
                    }
                    convertBtn.isEnabled = true
                }
            } catch (e: Exception) {
                runOnUiThread {
                    statusText.text = "오디오 추출 실패: ${e.message}"
                    resultText.visibility = View.GONE
                    convertBtn.isEnabled = true
                }
            }
        }.start()
    }
}
