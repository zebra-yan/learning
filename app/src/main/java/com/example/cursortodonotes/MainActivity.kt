package com.example.cursortodonotes

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

/**
 * 核心概念说明：
 * - @Composable：标记一个可被 Jetpack Compose 渲染的 UI 函数。它描述界面应该长什么样，
 *   当状态变化时 Compose 会自动触发重组（recomposition），重新执行相关函数以刷新 UI。
 * - State：驱动 UI 的数据源；UI = f(state)。这里使用 mutableStateOf / mutableStateListOf
 *   创建可观察状态，状态一改，对应 UI 自动更新。
 * - remember：在重组之间记住值，避免每次重组都重新初始化。例如 screenState、notes、nextId
 *   如果没有 remember，重组时这些变量会被重置，导致输入框内容丢失或列表被清空。
 */
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF0061A4),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFD1E4FF),
    onPrimaryContainer = Color(0xFF001D36),
    // 改进：显式指定背景与表面色，深浅色切换时更一致，避免使用系统默认的不确定性。
    background = Color(0xFFF8F9FF),
    surface = Color(0xFFF8F9FF)
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF9ECAFF),
    onPrimary = Color(0xFF003258),
    primaryContainer = Color(0xFF00497D),
    onPrimaryContainer = Color(0xFFD1E4FF)
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    TodoNotesApp()
                }
            }
        }
    }
}

/**
 * TodoNote：业务数据模型（领域对象）。
 * - id：唯一标识，用于定位/编辑/删除/列表 key。
 * - title / content：标题与正文。
 * - timestamp：最后更新时间，当前先存着，后续可用于排序或显示时间。
 * - isDone：完成状态，用于 Checkbox 勾选。
 * 后续迁移 Room 时几乎可直接变成 @Entity。
 */
data class TodoNote(
    val id: Long,
    val title: String,
    val content: String,
    val timestamp: Long,
    val isDone: Boolean
)

/**
 * 页面路由状态：用密封类型管理当前页面（列表/详情），替代导航库的最小路由实现。
 * Detail.noteId 为 null 表示新建，非 null 表示编辑指定 id 的条目。
 * 使用 data object 而非普通 object，与 data class 统一，且便于调试时生成 toString。
 */
private sealed interface ScreenState {
    data object List : ScreenState
    data class Detail(val noteId: Long?) : ScreenState
}

/**
 * 应用状态中心：持有所有内存态，并负责页面路由分发。
 * 所有状态放在根层，子组件通过回调触发状态变更，符合“状态向下传递、事件向上回调”。
 */
@Composable
private fun TodoNotesApp() {
    // 内存中的 TodoNote 列表；mutableStateListOf 让列表项增删改都能被 Compose 观察。
    val notes = remember {
        mutableStateListOf(
            TodoNote(
                id = 1L,
                title = "Welcome to Cursor TodoNotes",
                content = "Tap an item to edit it, or use + to create one.",
                timestamp = System.currentTimeMillis(),
                isDone = false
            )
        )
    }

    // 自增 id 生成器，用于新建条目时保证唯一性。
    var nextId by remember { mutableStateOf(2L) }

    // 当前页面状态：列表或详情（详情携带待编辑条目 id，null 表示新建）。
    var screenState by remember { mutableStateOf<ScreenState>(ScreenState.List) }

    // 改进：在详情页拦截系统返回键，点按返回时回到列表页而非直接退出应用。
    if (screenState is ScreenState.Detail) {
        BackHandler { screenState = ScreenState.List }
    }

    when (val current = screenState) {
        // 列表页：展示所有条目，并提供增/删/改查（完成切换）的入口。
        ScreenState.List -> TodoListScreen(
            notes = notes,
            onAdd = { screenState = ScreenState.Detail(noteId = null) },
            onToggleDone = { noteId ->
                // 完成状态切换：通过 indexOfFirst 定位，再用 copy 替换元素触发观察更新。
                // 先缓存 old 避免对列表重复索引读取。
                val index = notes.indexOfFirst { it.id == noteId }
                if (index >= 0) {
                    val old = notes[index]
                    notes[index] = old.copy(isDone = !old.isDone)
                }
            },
            onDelete = { noteId ->
                // 删除：按 id 移除所有匹配项。
                notes.removeAll { it.id == noteId }
            },
            onOpenDetail = { noteId ->
                // 打开编辑：进入详情页并携带目标 id。
                screenState = ScreenState.Detail(noteId = noteId)
            }
        )

        // 详情页：根据 noteId 是否为 null 区分新建与编辑。
        is ScreenState.Detail -> {
            val existing = notes.firstOrNull { it.id == current.noteId }
            TodoDetailScreen(
                note = existing,
                onBack = { screenState = ScreenState.List },
                onSave = { title, content ->
                    val now = System.currentTimeMillis()
                    val editingId = current.noteId
                    if (editingId == null) {
                        // 新增：生成新 id 并追加到列表。
                        notes.add(
                            TodoNote(
                                id = nextId++,
                                title = title,
                                content = content,
                                timestamp = now,
                                isDone = false
                            )
                        )
                    } else {
                        // 编辑：找到对应下标后用 copy 更新字段（含 timestamp）。
                        val index = notes.indexOfFirst { it.id == editingId }
                        if (index >= 0) {
                            notes[index] = notes[index].copy(
                                title = title,
                                content = content,
                                timestamp = now
                            )
                        }
                    }
                    screenState = ScreenState.List
                },
                onDelete = {
                    // 详情页删除：编辑态才允许删除。
                    current.noteId?.let { targetId ->
                        notes.removeAll { it.id == targetId }
                    }
                    screenState = ScreenState.List
                }
            )
        }
    }
}

/**
 * 列表页：Scaffold 提供 TopBar + FAB，LazyColumn 展示条目。
 * 空列表时显示 EmptyState；每个条目用 TodoNoteCard 展示。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TodoListScreen(
    notes: List<TodoNote>,
    onAdd: () -> Unit,
    onToggleDone: (Long) -> Unit,
    onDelete: (Long) -> Unit,
    onOpenDetail: (Long) -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Todo + Notes") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onAdd) {
                // 改进：使用 Material 图标与 contentDescription，更符合规范且支持无障碍。
                Icon(Icons.Default.Add, contentDescription = "Add")
            }
        }
    ) { padding ->
        if (notes.isEmpty()) {
            EmptyState(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(notes, key = { it.id }) { note ->
                    TodoNoteCard(
                        note = note,
                        onToggleDone = { onToggleDone(note.id) },
                        onDelete = { onDelete(note.id) },
                        onClick = { onOpenDetail(note.id) }
                    )
                }
            }
        }
    }
}

/** 空列表占位提示。 */
@Composable
private fun EmptyState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier,
        // 改进：同时水平与垂直居中，空状态视觉更平衡。
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "No items yet",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "Tap + to add your first todo or note.",
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

/**
 * 单个列表项卡片：展示标题、内容摘要、完成 Checkbox 和删除按钮。
 * 点击整卡进入编辑详情。
 */
@Composable
private fun TodoNoteCard(
    note: TodoNote,
    onToggleDone: () -> Unit,
    onDelete: () -> Unit,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        // 改进：给卡片加轻微背景色区分，列表项层次更清晰。
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            // 改进：让行内元素垂直居中，避免文字与复选框顶部不对齐。
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // 改进：移除 Checkbox 的固定 24.dp 尺寸，保留默认触控区域，避免点击困难。
            Checkbox(
                checked = note.isDone,
                onCheckedChange = { onToggleDone() }
            )
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = note.title.ifBlank { "(Untitled)" },
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                // 改进：仅在内容非空时显示摘要，避免空内容时显示 "No content" 占位。
                if (note.content.isNotBlank()) {
                    Text(
                        text = note.content,
                        style = MaterialTheme.typography.bodyMedium,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            // 改进：使用图标按钮替代文字按钮，更紧凑且更符合 Material 3 习惯。
            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Default.Delete,
                    contentDescription = "Delete",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

/**
 * 详情页：新建或编辑 TodoNote。
 * 使用 remember(note?.id) 在切换不同条目时重置输入框，避免复用旧值。
 * 保存时通过 noteId 区分新建与编辑；编辑态才显示删除按钮。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TodoDetailScreen(
    note: TodoNote?,
    onBack: () -> Unit,
    onSave: (title: String, content: String) -> Unit,
    onDelete: () -> Unit
) {
    // 以 note.id 作为 remember 的 key，切换条目时自动重置输入状态。
    var title by remember(note?.id) { mutableStateOf(note?.title.orEmpty()) }
    var content by remember(note?.id) { mutableStateOf(note?.content.orEmpty()) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (note == null) "New Item" else "Edit Item") },
                // 改进：在 TopAppBar 提供返回箭头，符合 Android 标准返回交互。
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                // 改进：将删除按钮放到 TopBar actions，编辑态才可见，节省底部空间并减少误触。
                actions = {
                    if (note != null) {
                        IconButton(onClick = onDelete) {
                            Icon(Icons.Default.Delete, contentDescription = "Delete")
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Title") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            OutlinedTextField(
                value = content,
                onValueChange = { content = it },
                label = { Text("Content") },
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            )
            // 改进：底部只保留 Save 按钮，视觉焦点更集中；返回/删除已迁移到 TopAppBar。
            Button(
                onClick = { onSave(title.trim(), content.trim()) },
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.medium
            ) {
                Text("Save")
            }
        }
    }
}
