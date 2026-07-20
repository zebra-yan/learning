# Cursor Todo Notes

一个用于学习 Cursor 与 Android 开发流程的示例项目。  
当前已实现从 0 到 1 的 Kotlin + Jetpack Compose 应用：包含 Todo/Note 列表页、详情页，以及内存中的增删改查（CRUD）逻辑。后续将逐步加入数据层、测试和网络层。

## 1. 技术栈与实现思路

- Language: Kotlin
- Build: Gradle Kotlin DSL (`*.kts`)
- UI: Jetpack Compose + Material 3
- Android: `minSdk 24`, `targetSdk 34`, Java/Kotlin 17
- 当前实现策略:
  - 单 Activity + Compose 负责 UI 渲染
  - 列表页 + 详情页，支持新增、编辑、删除、完成状态切换
  - 数据暂存内存，后续逐步接入 Room、Retrofit 和测试

## 2. 目录结构（核心）

```text
.
├─ build.gradle.kts
├─ settings.gradle.kts
├─ gradle.properties
└─ app
   ├─ build.gradle.kts
   ├─ proguard-rules.pro
   └─ src
      └─ main
         ├─ AndroidManifest.xml
         ├─ java/com/example/cursortodonotes/MainActivity.kt
         └─ res/values
            ├─ strings.xml
            ├─ colors.xml
            └─ themes.xml
```

## 3. 文件级说明（作用 + 实现方式）

### 根目录

#### `settings.gradle.kts`
- **作用**: 声明工程名、模块列表和仓库解析策略。
- **实现方式**:
  - `pluginManagement` 指定插件仓库（`google`, `mavenCentral`, `gradlePluginPortal`）。
  - `dependencyResolutionManagement` 统一依赖仓库。
  - `include(":app")` 注册应用模块。

#### `build.gradle.kts`
- **作用**: 根工程插件版本集中管理。
- **实现方式**:
  - 只声明插件版本并 `apply false`，由子模块按需启用。
  - 便于后续多模块扩展时统一版本。

#### `gradle.properties`
- **作用**: Gradle 与 Android 构建全局参数。
- **实现方式**:
  - 配置 JVM 内存、UTF-8 编码。
  - 启用 AndroidX 与 Jetifier。
  - 指定 Kotlin 官方代码风格。

---

### `app` 模块

#### `app/build.gradle.kts`
- **作用**: Android App 模块的核心构建脚本。
- **实现方式**:
  - 启用 `com.android.application` 与 `org.jetbrains.kotlin.android`。
  - 在 `android` 块中配置:
    - `namespace` / `applicationId`
    - SDK 版本、`versionCode`、`versionName`
    - `buildTypes`（release 关闭混淆）
    - Java/Kotlin 17 编译目标
    - `buildFeatures { compose = true }`
  - 在 `dependencies` 中引入:
    - Compose BOM 与 UI 依赖
    - Material3
    - Activity Compose
    - JUnit / AndroidX Test / Compose UI Test
    - Material Components (用于 XML 主题支持)

#### `app/proguard-rules.pro`
- **作用**: release 混淆与保留规则文件。
- **实现方式**:
  - 当前保持最小占位，后续若引入反射/序列化框架再补充 keep 规则。

---

### Android 入口与资源

#### `app/src/main/AndroidManifest.xml`
- **作用**: Android 组件注册与应用级配置。
- **实现方式**:
  - 声明应用主题 `@style/Theme.CursorTodoNotes`。
  - 注册 `MainActivity` 并设置 `MAIN/LAUNCHER` 作为启动入口。

#### `app/src/main/java/com/example/cursortodonotes/MainActivity.kt`
- **作用**: 应用入口 Activity，承载 Compose UI 与全部业务状态。
- **实现方式**:
  - `ComponentActivity` + `setContent {}`。
  - 自定义 `AppTheme` 提供深浅色方案。
  - `TodoNotesApp` 作为根状态中心，持有 `notes`、`nextId`、`screenState`。
  - 根据 `ScreenState` 分发列表页 `TodoListScreen` 或详情页 `TodoDetailScreen`。
  - 在内存中实现增删改查：新增用 `nextId` 生成条目；编辑通过 `indexOfFirst` + `copy` 更新；删除用 `removeAll`；完成状态切换也是 Update 的一种。
  - 代码中包含对 `@Composable`、`remember`、`State`、`TodoNote` 模型和 CRUD 逻辑的详细注释。

#### `app/src/main/res/values/strings.xml`
- **作用**: 字符串资源管理。
- **实现方式**:
  - 当前定义 `app_name`，供 Manifest 与系统展示使用。

#### `app/src/main/res/values/colors.xml`
- **作用**: 颜色资源定义。
- **实现方式**:
  - 定义了一组基础颜色资源。

#### `app/src/main/res/values/themes.xml`
- **作用**: 应用主题定义（XML 侧）。
- **实现方式**:
  - 主题继承 `Theme.Material3.DayNight.NoActionBar`。
  - 与 Compose `MaterialTheme` 搭配，支持 Material 3 风格与深浅色切换。
  - 配置了状态栏颜色等基础属性。

## 4. 如何运行

1. 用 Android Studio 打开项目根目录。  
2. 等待 Gradle Sync 完成。  
3. 选择 `app` 模块，运行 `debug` 到模拟器或真机。  
4. 首次运行期望结果：应用展示 "Todo + Notes" 列表页，默认有一条欢迎条目；可点击 + 新增、点击条目编辑、勾选切换完成状态、点击 Delete 删除。

## 5. 测试说明

当前可用测试类型:
- JVM 单元测试：`app/src/test`（待创建）
- 仪器测试/UI 测试：`app/src/androidTest`（待创建）

本项目目前**不依赖必填环境变量**即可编译运行。  
若后续接入真实后端，可新增：
- `BASE_URL`
- `API_TOKEN`
- `ENV`（`dev`/`staging`/`prod`）

## 6. 后续迭代路线（与学习计划对齐）

1. ✅ 第 2 阶段：已实现 Todo/Note 列表与详情页面，用内存数据跑通增删改查。 
                当你切换系统深色/浅色主题时，Android 会触发 uiMode 配置变化，默认行为是销毁并重建 MainActivity。重建后 Compose 树重新创建，remember { mutableStateListOf(...) } 被重新初始化，新建的便签因此消失。旋转屏幕、改变字号/语言等配置变化也会触发同样问题。
2. 第 3 阶段：接入 Room，保证重启后数据保留，并补 3-5 个单测。  
3. 第 4 阶段：预留 Retrofit 接口 + Repository 解耦 + README 持续完善。  

## 7. 常见问题

### 资源链接错误（`resource ... not found`）
- 多见于主题属性不匹配（Material2/Material3 混用）或依赖未同步。
- 处理顺序建议:
  1. 检查 `themes.xml` 中属性是否存在于当前主题体系。
  2. 确认 `app/build.gradle.kts` 已包含 Material 相关依赖。
  3. `Sync Project with Gradle Files` 后重建项目。
