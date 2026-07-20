package com.example.cursortodonotes

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ScheduleParserTest {
    @Test
    fun `parseScheduleMarkdownToTodoNotes returns day sections as notes`() {
        val markdown = """
### 📅 周一：战略与市场（定位之日）
*   **核心逻辑**：先 look 路，再 pull 车。
*   **上午（09:00 - 12:00）**：**市场坐标锚点**。
### 📅 周二：核心构建（骨架之日）
*   **核心逻辑**：在脑力最旺盛时处理最硬核的逻辑。
""".trimIndent()

        val notes = parseScheduleMarkdownToTodoNotes(markdown)

        assertEquals(2, notes.size)
        assertEquals("周一：战略与市场（定位之日）", notes[0].title)
        assertTrue(notes[0].content.contains("核心逻辑"))
        assertEquals("周二：核心构建（骨架之日）", notes[1].title)
        assertTrue(notes[1].content.contains("脑力最旺盛"))
    }
}
