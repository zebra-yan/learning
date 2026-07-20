package com.example.cursortodonotes

/**
 * 解析周计划 Markdown 文本，并将每个日程节转换为 TodoNote。
 *
 * 目前支持将三级标题（###）作为单独的日程段落，并将段落内的列表项作为 note 内容。
 */
fun parseScheduleMarkdownToTodoNotes(markdown: String): List<TodoNote> {
    val notes = mutableListOf<TodoNote>()
    var currentTitle: String? = null
    val currentContent = mutableListOf<String>()

    fun flushCurrentSection() {
        if (currentTitle != null) {
            val content = currentContent.joinToString("\n") { it.trimEnd() }.trim()
            notes += TodoNote(
                id = 0L,
                title = currentTitle!!,
                content = content,
                timestamp = 0L,
                isDone = false
            )
        }
        currentTitle = null
        currentContent.clear()
    }

    markdown.lineSequence().forEach { rawLine ->
        val line = rawLine.trim()
        when {
            line.startsWith("###") -> {
                flushCurrentSection()
                currentTitle = line.removePrefix("###").trim().removePrefix("📅").trim().removePrefix("：").trim()
            }
            currentTitle != null && (line.startsWith("*") || line.startsWith("-") || line.matches(Regex("^\\d+\\..*"))) -> {
                currentContent += line.removePrefix("*").removePrefix("-").trimStart().trim()
            }
            currentTitle != null && line.isNotEmpty() -> {
                currentContent += line
            }
            else -> {
                // ignore blank or unrelated lines
            }
        }
    }
    flushCurrentSection()
    return notes
}
