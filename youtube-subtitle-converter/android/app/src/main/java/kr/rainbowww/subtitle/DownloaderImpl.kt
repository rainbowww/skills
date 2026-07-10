package kr.rainbowww.subtitle

import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import org.schabi.newpipe.extractor.downloader.Downloader
import org.schabi.newpipe.extractor.downloader.Request
import org.schabi.newpipe.extractor.downloader.Response
import java.util.concurrent.TimeUnit

/** NewPipeExtractor가 쓰는 HTTP 다운로더 — OkHttp 구현. (2단계: 폰에서 유튜브 오디오 추출) */
class DownloaderImpl private constructor() : Downloader() {

    private val client: OkHttpClient = OkHttpClient.Builder()
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    override fun execute(request: Request): Response {
        val httpMethod = request.httpMethod()
        val url = request.url()
        val headers = request.headers()
        val dataToSend = request.dataToSend()

        val requestBody = dataToSend?.toRequestBody(null, 0, dataToSend.size)

        val builder = okhttp3.Request.Builder()
            .method(httpMethod, requestBody)
            .url(url)
            .addHeader("User-Agent", USER_AGENT)

        for ((headerName, headerValueList) in headers) {
            if (headerValueList.size > 1) {
                builder.removeHeader(headerName)
                for (headerValue in headerValueList) builder.addHeader(headerName, headerValue)
            } else if (headerValueList.size == 1) {
                builder.header(headerName, headerValueList[0])
            }
        }

        val response = client.newCall(builder.build()).execute()
        val body = response.body?.string()
        val latestUrl = response.request.url.toString()
        return Response(
            response.code,
            response.message,
            response.headers.toMultimap(),
            body,
            latestUrl
        )
    }

    companion object {
        private const val USER_AGENT =
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

        @Volatile
        private var instance: DownloaderImpl? = null

        fun getInstance(): DownloaderImpl =
            instance ?: synchronized(this) {
                instance ?: DownloaderImpl().also { instance = it }
            }
    }
}
