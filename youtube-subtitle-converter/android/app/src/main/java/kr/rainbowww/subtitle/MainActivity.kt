package kr.rainbowww.subtitle

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/**
 * 자막 변환기 — 독립 안드로이드 앱(폰만으로 동작 목표).
 *
 * 단계별 개발:
 *  1) (현재) 설치되는 진짜 APK + 화면 + 유튜브 주소 인식.  ← CI가 빌드/설치 검증
 *  2) NewPipeExtractor 로 폰에서 오디오 추출.
 *  3) whisper.cpp 온디바이스 한국어 음성 인식 → 자막.
 * 웹앱의 `youtube_parser.parse_video_id` 정규식을 그대로 옮겨 동작을 일치시킴.
 */
class MainActivity : AppCompatActivity() {

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
                resultText.visibility = TextView.GONE
                return@setOnClickListener
            }
            statusText.text = "영상 인식 완료 (ID: $id)"
            resultText.visibility = TextView.VISIBLE
            resultText.text =
                "이 버전은 설치·화면 확인용입니다.\n" +
                "다음 업데이트에서 폰 안에서의 오디오 추출과 한국어 음성 인식이 추가됩니다.\n\n" +
                "PC가 있다면 지금 바로 쓰려면: 웹앱(자막 변환기)을 PC에서 실행하고 폰 브라우저로 접속하세요."
        }
    }
}
