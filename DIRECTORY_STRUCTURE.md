# art-design-pro

> Generated on 2026-04-13

## Directory Structure

```
art-design-pro/
├── backend/
│   ├── .idea/
│   │   ├── inspectionProfiles/
│   │   │   ├── profiles_settings.xml
│   │   │   └── Project_Default.xml
│   │   ├── employment-backend.iml
│   │   ├── misc.xml
│   │   ├── modules.xml
│   │   ├── vcs.xml
│   │   └── workspace.xml
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 20260330_add_company_activities_and_announcements.py
│   │   │   ├── 20260330_add_company_verified_index.py
│   │   │   ├── 20260330_add_job_description_indexes.py
│   │   │   ├── 20260330_add_student_profile_indexes.py
│   │   │   ├── 20260401_add_activity_type_name.py
│   │   │   └── fb44549e9882_initial.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── admin.py
│   │   │       ├── ai.py
│   │   │       ├── auth.py
│   │   │       ├── company.py
│   │   │       ├── router.py
│   │   │       ├── school.py
│   │   │       └── student.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── redis_client.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── ai_record.py
│   │   │   ├── base.py
│   │   │   ├── college_employment.py
│   │   │   ├── company_activity.py
│   │   │   ├── company_announcement.py
│   │   │   ├── company_profile_pending.py
│   │   │   ├── company.py
│   │   │   ├── employment_warning.py
│   │   │   ├── job.py
│   │   │   ├── knowledge_doc.py
│   │   │   ├── operation_log.py
│   │   │   ├── refresh_token.py
│   │   │   ├── regional_flow.py
│   │   │   ├── scarce_talent.py
│   │   │   ├── student.py
│   │   │   ├── system_config.py
│   │   │   └── university.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── ai.py
│   │   │   ├── auth.py
│   │   │   ├── common.py
│   │   │   ├── company_activity.py
│   │   │   ├── company_announcement.py
│   │   │   ├── company.py
│   │   │   ├── school.py
│   │   │   └── student.py
│   │   ├── services/
│   │   │   ├── document/
│   │   │   │   ├── __init__.py
│   │   │   │   └── resume_parser.py
│   │   │   ├── rag/
│   │   │   │   ├── __init__.py
│   │   │   │   └── rag_service.py
│   │   │   ├── __init__.py
│   │   │   ├── activity_service.py
│   │   │   ├── admin_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── announcement_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── company_service.py
│   │   │   ├── data_generator.py
│   │   │   ├── resume_export.py
│   │   │   ├── scarce_talent_analyzer.py
│   │   │   ├── school_service.py
│   │   │   ├── stats_service.py
│   │   │   └── student_service.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── cleaning.py
│   │   │   ├── education_mapper.py
│   │   │   ├── industry_normalizer.py
│   │   │   ├── province_normalizer.py
│   │   │   └── salary_parser.py
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── main.py
│   ├── migrations/
│   │   ├── 001_add_import_tables.sql
│   │   └── 002_add_company_profile_pending.sql
│   ├── scripts/
│   │   └── generate_companies_and_jobs.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_admin_stats.py
│   │   ├── test_cleaning_functions.py
│   │   ├── test_company_activities.py
│   │   └── test_company_announcements.py
│   ├── uploads/
│   │   └── resumes/
│   │       ├── resume_40d74cb6_5030b4a3d7a14142aee377b6bf4be8a8.docx
│   │       ├── resume_40d74cb6_5213cfd70968403b84eba8c5923f6af5.docx
│   │       ├── resume_40d74cb6_8376428274aa4a55b6ef24742df00d48.docx
│   │       └── resume_40d74cb6_91694ac309de45678ed1d414763cc214.docx
│   ├── alembic.ini
│   ├── data.db
│   ├── docker-compose.yml
│   ├── employment.db
│   ├── import_school_data.py
│   ├── migrate_to_sqlite.py
│   ├── PERFORMANCE_ANALYSIS.md
│   ├── requirements.txt
│   ├── schema.sqlite.sql
│   ├── start.bat
│   ├── start.sh
│   ├── students_import_template.csv
│   └── test_login.ps1
├── dataset/
│   ├── 学校数据/
│   │   ├── 1.各学历去向落实率(基数确定+就业过程数据).csv
│   │   ├── 2.各学历去向落实率(过程数据).csv
│   │   ├── 3.各学院去向落实情况统计表(过程数据).csv
│   │   ├── 4.各学院去向落实情况统计表(基数确定+就业过程数据).csv
│   │   ├── 5.各学历毕业去向分类统计(含升学-过程数据).csv
│   │   ├── 6.区域流向情况统计表.csv
│   │   ├── 7.各学历毕业去向分类统计(含升学-基数确定+就业过程).csv
│   │   ├── 8.各学院毕业去向分类统计(含升学-过程数据).csv
│   │   └── 9.各学院毕业去向与落实情况合并表.csv
│   ├── train_data/
│   │   ├── table1_user.csv
│   │   ├── table2_jd_part1.csv
│   │   ├── table2_jd_part2.csv
│   │   ├── table2_jd_part3.csv
│   │   └── table3_action.csv
│   ├── zhaopin_round1_test_20190716/
│   │   ├── user_ToBePredicted.csv
│   │   ├── zhaopin_round1_user_exposure_A_20190723.csv
│   │   └── zhaopin_round1_user_exposure_B_20190819.csv
│   ├── 200711.CSV
│   ├── 大学生毕业就业选择样例数据_10000条.csv
│   ├── 大学生就业选择.csv
│   └── 字段说明.docx
├── docs/
│   ├── superpowers/
│   │   └── plans/
│   │       └── 2026-03-30-company-activity-management.md
│   ├── 操作手册.md
│   ├── 前端开发指南.md
│   ├── 前后端对接说明.md
│   ├── AI_RAG_需求文档.md
│   ├── ARCHITECTURE.md
│   ├── CLAUDE_CODE_OPTIMIZATION.md
│   ├── cleaning-rules.md
│   ├── data-analysis-report.md
│   ├── data-dictionary.md
│   ├── database-schema.md
│   ├── import-log.md
│   ├── import-plan.md
│   ├── plan.md
│   ├── PROJECT_GUIDE.md
│   ├── README.md
│   └── vite-proxy-delay.md
├── example/
│   ├── example_files/
│   │   ├── CQU.png
│   │   ├── index-DfDDTphO.css
│   │   ├── index-DM_UX8fa.js.下载
│   │   └── map-vendor-DwUhsmFz.css
│   └── example.html
├── public/
│   ├── bg/
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   ├── 3.jpg
│   │   ├── 4.jpg
│   │   ├── 5.jpg
│   │   ├── 6.jpg
│   │   ├── 7.jpg
│   │   ├── 8.jpg
│   │   └── 9.jpg
│   ├── bg2/
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   ├── 3.jpg
│   │   ├── 4.jpg
│   │   ├── 5.jpg
│   │   └── 6.jpg
│   ├── favicon.ico
│   ├── icon.svg
│   ├── icon2.svg
│   ├── u1.png
│   └── u2.jpg
├── RAG/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── history.py
│   │   ├── job_recommend.py
│   │   ├── qa.py
│   │   ├── resume_optimize.py
│   │   ├── resume_parse.py
│   │   └── upload.py
│   ├── chat_history/
│   │   └── user_001
│   ├── chroma_db/
│   │   ├── 59148bc4-0d25-4745-ace6-29d61c168c8c/
│   │   │   ├── data_level0.bin
│   │   │   ├── header.bin
│   │   │   ├── index_metadata.pickle
│   │   │   ├── length.bin
│   │   │   └── link_lists.bin
│   │   └── chroma.sqlite3
│   ├── data/
│   │   ├── 尺码推荐.txt
│   │   ├── 洗涤养护.txt
│   │   ├── 颜色选择.txt
│   │   └── rag_sqlite.db
│   ├── db/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── knowledge.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   └── knowledge_repo.py
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── init_db.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py
│   │   └── response.py
│   ├── services/
│   │   ├── chat/
│   │   │   ├── __init__.py
│   │   │   ├── db_history_service.py
│   │   │   └── history_service.py
│   │   ├── chat_history/
│   │   │   ├── 007c32a4-cfc2-4981-914a-493efd811476.json
│   │   │   ├── 0c1d7568-f535-47dd-8554-7be12f6fb378.json
│   │   │   ├── 16ad2152-9153-46b4-b4c4-1489f8926433.json
│   │   │   ├── 286ca0fc-db19-4577-a9cf-f0192a2ea638.json
│   │   │   ├── 29b0c3c0-2fce-4316-a002-456b58d253fb.json
│   │   │   ├── 2e114e7d-b0a5-4a5b-81e9-3c90bc6d8254.json
│   │   │   ├── 5ce2bb11-d4f9-4b6d-923e-8f3fc18b26b0.json
│   │   │   ├── 6aaa3513-168d-46fd-b9d4-f8bc92918966.json
│   │   │   ├── 6ededa59-6bc1-4865-888b-d70239069cb2.json
│   │   │   ├── 8327a248-6265-4537-92d8-9869cd1422e1.json
│   │   │   ├── 88034387-0c6b-4139-804c-c96f2a0e2e3b.json
│   │   │   ├── 9c7b4b6c-f4a0-4ecb-922a-eef3e75862ad.json
│   │   │   ├── abb21df6-2ef1-491c-8f5b-db07e7c24ead.json
│   │   │   ├── b9c2ca14-1a93-4bc7-bf9b-b01b682b6a82.json
│   │   │   ├── d526ba9a-2bf1-47c2-b7b2-15e8c708ff98.json
│   │   │   ├── d5aec1e5-f1ff-49b1-817b-aed56eb735a3.json
│   │   │   ├── d8217bde-e928-4cb6-856a-90820b56bf04.json
│   │   │   ├── def7beb9-d783-469d-8e9b-32a7bc74d2a1.json
│   │   │   └── e2094146-85ff-4c5e-864b-a9a1a71b9181.json
│   │   ├── document/
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_sync.py
│   │   │   ├── parser.py
│   │   │   └── resume_parser.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── factory.py
│   │   │   └── tongyi_adapter.py
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── context_assembler.py
│   │   │   ├── job_recommend.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rag_engine.py
│   │   │   ├── resume_optimize.py
│   │   │   ├── structured_query.py
│   │   │   └── vector_search.py
│   │   └── __init__.py
│   ├── app_file_uploader.py
│   ├── app_qa.py
│   ├── app.py
│   ├── chroma.sqlite3
│   ├── config_data.py
│   ├── employment.db
│   ├── file_history_store.py
│   ├── index_jobs.py
│   ├── knowledge_base.py
│   ├── md5.text
│   ├── rag.py
│   ├── README.md
│   ├── requirements.txt
│   └── vector_stores.py
├── scripts/
│   ├── clean-dev.ts
│   └── generate-dir-tree.cjs
├── src/
│   ├── api/
│   │   ├── admin.ts
│   │   ├── ai.ts
│   │   ├── auth.ts
│   │   ├── company_activity.ts
│   │   ├── company_announcement.ts
│   │   ├── company.ts
│   │   ├── school.ts
│   │   ├── stats.ts
│   │   ├── student.ts
│   │   └── system-manage.ts
│   ├── assets/
│   │   ├── images/
│   │   │   ├── 3d/
│   │   │   │   ├── icon1.webp
│   │   │   │   ├── icon2.webp
│   │   │   │   ├── icon3.webp
│   │   │   │   ├── icon4.webp
│   │   │   │   ├── icon5.webp
│   │   │   │   ├── icon6.webp
│   │   │   │   ├── icon7.webp
│   │   │   │   └── icon8.webp
│   │   │   ├── avatar/
│   │   │   │   ├── avatar.webp
│   │   │   │   ├── avatar1.webp
│   │   │   │   ├── avatar10.webp
│   │   │   │   ├── avatar2.webp
│   │   │   │   ├── avatar3.webp
│   │   │   │   ├── avatar4.webp
│   │   │   │   ├── avatar5.webp
│   │   │   │   ├── avatar6.webp
│   │   │   │   ├── avatar7.webp
│   │   │   │   ├── avatar8.webp
│   │   │   │   └── avatar9.webp
│   │   │   ├── ceremony/
│   │   │   │   ├── hb.png
│   │   │   │   ├── sd.png
│   │   │   │   ├── xc.png
│   │   │   │   └── yd.png
│   │   │   ├── common/
│   │   │   │   └── logo.webp
│   │   │   ├── cover/
│   │   │   │   ├── img1.webp
│   │   │   │   ├── img10.webp
│   │   │   │   ├── img2.webp
│   │   │   │   ├── img3.webp
│   │   │   │   ├── img4.webp
│   │   │   │   ├── img5.webp
│   │   │   │   ├── img6.webp
│   │   │   │   ├── img7.webp
│   │   │   │   ├── img8.webp
│   │   │   │   └── img9.webp
│   │   │   ├── draw/
│   │   │   │   └── draw1.png
│   │   │   ├── lock/
│   │   │   │   ├── bg_dark.webp
│   │   │   │   └── bg_light.webp
│   │   │   ├── login/
│   │   │   │   └── lf_icon2.webp
│   │   │   ├── safeguard/
│   │   │   │   └── server.png
│   │   │   ├── settings/
│   │   │   │   ├── menu_layouts/
│   │   │   │   │   ├── dual_column.png
│   │   │   │   │   ├── horizontal.png
│   │   │   │   │   ├── mixed.png
│   │   │   │   │   └── vertical.png
│   │   │   │   ├── menu_styles/
│   │   │   │   │   ├── dark.png
│   │   │   │   │   ├── design.png
│   │   │   │   │   └── light.png
│   │   │   │   └── theme_styles/
│   │   │   │       ├── dark.png
│   │   │   │       ├── light.png
│   │   │   │       └── system.png
│   │   │   ├── svg/
│   │   │   │   ├── 403.svg
│   │   │   │   ├── 404.svg
│   │   │   │   ├── 500.svg
│   │   │   │   └── login_icon.svg
│   │   │   ├── user/
│   │   │   │   ├── avatar.webp
│   │   │   │   └── bg.webp
│   │   │   └── favicon.ico
│   │   ├── styles/
│   │   │   ├── core/
│   │   │   │   ├── app.scss
│   │   │   │   ├── dark.scss
│   │   │   │   ├── el-dark.scss
│   │   │   │   ├── el-light.scss
│   │   │   │   ├── el-ui.scss
│   │   │   │   ├── md.scss
│   │   │   │   ├── mixin.scss
│   │   │   │   ├── reset.scss
│   │   │   │   ├── router-transition.scss
│   │   │   │   ├── tailwind.css
│   │   │   │   ├── theme-animation.scss
│   │   │   │   └── theme-change.scss
│   │   │   ├── custom/
│   │   │   │   ├── one-dark-pro.scss
│   │   │   │   └── project.scss
│   │   │   └── index.scss
│   │   └── svg/
│   │       └── loading.ts
│   ├── components/
│   │   ├── business/
│   │   │   └── comment-widget/
│   │   │       ├── widget/
│   │   │       │   └── CommentItem.vue
│   │   │       └── index.vue
│   │   ├── core/
│   │   │   ├── banners/
│   │   │   │   ├── art-basic-banner/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-card-banner/
│   │   │   │       └── index.vue
│   │   │   ├── base/
│   │   │   │   ├── art-back-to-top/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-logo/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-svg-icon/
│   │   │   │       └── index.vue
│   │   │   ├── cards/
│   │   │   │   ├── art-bar-chart-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-data-list-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-donut-chart-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-image-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-job-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-line-chart-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-progress-card/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-stats-card/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-timeline-list-card/
│   │   │   │       └── index.vue
│   │   │   ├── charts/
│   │   │   │   ├── art-bar-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-bubble-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-dual-bar-compare-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-gauge-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-h-bar-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-k-line-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-line-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-map-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-radar-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-ring-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-scatter-chart/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-word-cloud/
│   │   │   │       └── index.vue
│   │   │   ├── forms/
│   │   │   │   ├── art-button-more/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-button-table/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-drag-verify/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-excel-export/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-excel-import/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-form/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-search-bar/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-wang-editor/
│   │   │   │       ├── index.vue
│   │   │   │       └── style.scss
│   │   │   ├── layouts/
│   │   │   │   ├── art-breadcrumb/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-chat-window/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-fast-enter/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-fireworks-effect/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-global-component/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-global-search/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-header-bar/
│   │   │   │   │   ├── widget/
│   │   │   │   │   │   └── ArtUserMenu.vue
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-menus/
│   │   │   │   │   ├── art-horizontal-menu/
│   │   │   │   │   │   ├── widget/
│   │   │   │   │   │   │   └── HorizontalSubmenu.vue
│   │   │   │   │   │   └── index.vue
│   │   │   │   │   ├── art-mixed-menu/
│   │   │   │   │   │   └── index.vue
│   │   │   │   │   └── art-sidebar-menu/
│   │   │   │   │       ├── widget/
│   │   │   │   │       │   └── SidebarSubmenu.vue
│   │   │   │   │       ├── index.vue
│   │   │   │   │       ├── style.scss
│   │   │   │   │       └── theme.scss
│   │   │   │   ├── art-notification/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-page-content/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-screen-lock/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-settings-panel/
│   │   │   │   │   ├── composables/
│   │   │   │   │   │   ├── useSettingsConfig.ts
│   │   │   │   │   │   ├── useSettingsHandlers.ts
│   │   │   │   │   │   ├── useSettingsPanel.ts
│   │   │   │   │   │   └── useSettingsState.ts
│   │   │   │   │   ├── widget/
│   │   │   │   │   │   ├── BasicSettings.vue
│   │   │   │   │   │   ├── BoxStyleSettings.vue
│   │   │   │   │   │   ├── ColorSettings.vue
│   │   │   │   │   │   ├── ContainerSettings.vue
│   │   │   │   │   │   ├── MenuLayoutSettings.vue
│   │   │   │   │   │   ├── MenuStyleSettings.vue
│   │   │   │   │   │   ├── SectionTitle.vue
│   │   │   │   │   │   ├── SettingActions.vue
│   │   │   │   │   │   ├── SettingDrawer.vue
│   │   │   │   │   │   ├── SettingHeader.vue
│   │   │   │   │   │   ├── SettingItem.vue
│   │   │   │   │   │   └── ThemeSettings.vue
│   │   │   │   │   ├── index.vue
│   │   │   │   │   └── style.scss
│   │   │   │   └── art-work-tab/
│   │   │   │       └── index.vue
│   │   │   ├── media/
│   │   │   │   ├── art-cutter-img/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-video-player/
│   │   │   │       └── index.vue
│   │   │   ├── others/
│   │   │   │   ├── art-menu-right/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-watermark/
│   │   │   │       └── index.vue
│   │   │   ├── tables/
│   │   │   │   ├── art-table/
│   │   │   │   │   ├── index.vue
│   │   │   │   │   └── style.scss
│   │   │   │   └── art-table-header/
│   │   │   │       └── index.vue
│   │   │   ├── text-effect/
│   │   │   │   ├── art-count-to/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── art-festival-text-scroll/
│   │   │   │   │   └── index.vue
│   │   │   │   └── art-text-scroll/
│   │   │   │       └── index.vue
│   │   │   ├── theme/
│   │   │   │   └── theme-svg/
│   │   │   │       └── index.vue
│   │   │   ├── views/
│   │   │   │   ├── exception/
│   │   │   │   │   └── ArtException.vue
│   │   │   │   ├── login/
│   │   │   │   │   ├── AuthTopBar.vue
│   │   │   │   │   └── LoginLeftView.vue
│   │   │   │   └── result/
│   │   │   │       └── ArtResultPage.vue
│   │   │   └── widget/
│   │   │       └── art-icon-button/
│   │   │           └── index.vue
│   │   └── school/
│   │       ├── dashboard/
│   │       │   └── ProvinceDetailModal.vue
│   │       └── databoard/
│   │           └── ProvinceDetailModal.vue
│   ├── config/
│   │   ├── assets/
│   │   │   └── images.ts
│   │   ├── modules/
│   │   │   ├── component.ts
│   │   │   ├── fastEnter.ts
│   │   │   ├── festival.ts
│   │   │   └── headerBar.ts
│   │   ├── index.ts
│   │   └── setting.ts
│   ├── directives/
│   │   ├── business/
│   │   │   ├── highlight.ts
│   │   │   └── ripple.ts
│   │   ├── core/
│   │   │   ├── auth.ts
│   │   │   └── roles.ts
│   │   └── index.ts
│   ├── enums/
│   │   ├── appEnum.ts
│   │   └── formEnum.ts
│   ├── hooks/
│   │   ├── core/
│   │   │   ├── useAppMode.ts
│   │   │   ├── useAuth.ts
│   │   │   ├── useCeremony.ts
│   │   │   ├── useChart.ts
│   │   │   ├── useCommon.ts
│   │   │   ├── useFastEnter.ts
│   │   │   ├── useHeaderBar.ts
│   │   │   ├── useLayoutHeight.ts
│   │   │   ├── useTable.ts
│   │   │   ├── useTableColumns.ts
│   │   │   ├── useTableHeight.ts
│   │   │   └── useTheme.ts
│   │   └── index.ts
│   ├── locales/
│   │   ├── langs/
│   │   │   ├── en.json
│   │   │   └── zh.json
│   │   └── index.ts
│   ├── mock/
│   │   ├── json/
│   │   │   └── chinaMap.json
│   │   ├── temp/
│   │   │   ├── articleList.ts
│   │   │   ├── commentDetail.ts
│   │   │   ├── commentList.ts
│   │   │   └── formData.ts
│   │   └── upgrade/
│   │       └── changeLog.ts
│   ├── plugins/
│   │   ├── echarts.ts
│   │   └── index.ts
│   ├── router/
│   │   ├── core/
│   │   │   ├── ComponentLoader.ts
│   │   │   ├── IframeRouteManager.ts
│   │   │   ├── index.ts
│   │   │   ├── MenuProcessor.ts
│   │   │   ├── RoutePermissionValidator.ts
│   │   │   ├── RouteRegistry.ts
│   │   │   ├── RouteTransformer.ts
│   │   │   └── RouteValidator.ts
│   │   ├── guards/
│   │   │   ├── afterEach.ts
│   │   │   └── beforeEach.ts
│   │   ├── modules/
│   │   │   ├── article.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── employment.ts
│   │   │   ├── examples.ts
│   │   │   ├── exception.ts
│   │   │   ├── help.ts
│   │   │   ├── index.ts
│   │   │   ├── result.ts
│   │   │   ├── safeguard.ts
│   │   │   ├── system.ts
│   │   │   ├── template.ts
│   │   │   └── widgets.ts
│   │   ├── routes/
│   │   │   ├── asyncRoutes.ts
│   │   │   └── staticRoutes.ts
│   │   ├── index.ts
│   │   └── routesAlias.ts
│   ├── store/
│   │   ├── modules/
│   │   │   ├── menu.ts
│   │   │   ├── setting.ts
│   │   │   ├── table.ts
│   │   │   ├── user.ts
│   │   │   └── worktab.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── api/
│   │   │   └── api.d.ts
│   │   ├── common/
│   │   │   ├── index.ts
│   │   │   └── response.ts
│   │   ├── component/
│   │   │   ├── chart.ts
│   │   │   └── index.ts
│   │   ├── config/
│   │   │   └── index.ts
│   │   ├── directive/
│   │   │   └── directive.d.ts
│   │   ├── import/
│   │   │   ├── auto-imports.d.ts
│   │   │   └── components.d.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── store/
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── utils/
│   │   ├── constants/
│   │   │   ├── index.ts
│   │   │   └── links.ts
│   │   ├── form/
│   │   │   ├── index.ts
│   │   │   ├── responsive.ts
│   │   │   └── validator.ts
│   │   ├── http/
│   │   │   ├── error.ts
│   │   │   ├── index.ts
│   │   │   └── status.ts
│   │   ├── navigation/
│   │   │   ├── index.ts
│   │   │   ├── jump.ts
│   │   │   ├── route.ts
│   │   │   └── worktab.ts
│   │   ├── socket/
│   │   │   └── index.ts
│   │   ├── storage/
│   │   │   ├── index.ts
│   │   │   ├── storage-config.ts
│   │   │   ├── storage-key-manager.ts
│   │   │   └── storage.ts
│   │   ├── sys/
│   │   │   ├── console.ts
│   │   │   ├── error-handle.ts
│   │   │   ├── index.ts
│   │   │   ├── mittBus.ts
│   │   │   └── upgrade.ts
│   │   ├── table/
│   │   │   ├── tableCache.ts
│   │   │   ├── tableConfig.ts
│   │   │   └── tableUtils.ts
│   │   ├── ui/
│   │   │   ├── animation.ts
│   │   │   ├── colors.ts
│   │   │   ├── emojo.ts
│   │   │   ├── iconify-loader.ts
│   │   │   ├── index.ts
│   │   │   ├── loading.ts
│   │   │   └── tabs.ts
│   │   ├── index.ts
│   │   └── router.ts
│   ├── views/
│   │   ├── admin/
│   │   │   ├── colleges/
│   │   │   │   └── index.vue
│   │   │   ├── companies/
│   │   │   │   └── index.vue
│   │   │   ├── dashboard/
│   │   │   │   └── index.vue
│   │   │   ├── databoard/
│   │   │   │   ├── components/
│   │   │   │   └── index.vue
│   │   │   ├── profile-review/
│   │   │   │   └── index.vue
│   │   │   └── settings/
│   │   │       └── index.vue
│   │   ├── article/
│   │   │   ├── comment/
│   │   │   │   └── index.vue
│   │   │   ├── detail/
│   │   │   │   └── index.vue
│   │   │   ├── list/
│   │   │   │   └── index.vue
│   │   │   └── publish/
│   │   │       └── index.vue
│   │   ├── auth/
│   │   │   ├── forget-password/
│   │   │   │   └── index.vue
│   │   │   ├── login/
│   │   │   │   ├── index.vue
│   │   │   │   └── style.css
│   │   │   └── register/
│   │   │       └── index.vue
│   │   ├── change/
│   │   │   └── log/
│   │   │       └── index.vue
│   │   ├── common/
│   │   │   └── password/
│   │   │       └── index.vue
│   │   ├── company/
│   │   │   ├── activities/
│   │   │   │   └── index.vue
│   │   │   ├── announcements/
│   │   │   │   └── index.vue
│   │   │   ├── dashboard/
│   │   │   │   └── index.vue
│   │   │   ├── databoard/
│   │   │   │   └── index.vue
│   │   │   ├── jobs/
│   │   │   │   └── index.vue
│   │   │   ├── post-job/
│   │   │   │   └── index.vue
│   │   │   ├── profile/
│   │   │   │   └── index.vue
│   │   │   └── resumes/
│   │   │       └── index.vue
│   │   ├── dashboard/
│   │   │   ├── analysis/
│   │   │   │   ├── modules/
│   │   │   │   │   ├── customer-satisfaction.vue
│   │   │   │   │   ├── sales-mapping-by-country.vue
│   │   │   │   │   ├── target-vs-reality.vue
│   │   │   │   │   ├── today-sales.vue
│   │   │   │   │   ├── top-products.vue
│   │   │   │   │   ├── total-revenue.vue
│   │   │   │   │   ├── visitor-insights.vue
│   │   │   │   │   └── volume-service-level.vue
│   │   │   │   └── index.vue
│   │   │   ├── console/
│   │   │   │   ├── modules/
│   │   │   │   │   ├── about-project.vue
│   │   │   │   │   ├── active-user.vue
│   │   │   │   │   ├── card-list.vue
│   │   │   │   │   ├── dynamic-stats.vue
│   │   │   │   │   ├── new-user.vue
│   │   │   │   │   ├── sales-overview.vue
│   │   │   │   │   └── todo-list.vue
│   │   │   │   └── index.vue
│   │   │   └── ecommerce/
│   │   │       ├── modules/
│   │   │       │   ├── annual-sales.vue
│   │   │       │   ├── banner.vue
│   │   │       │   ├── cart-conversion-rate.vue
│   │   │       │   ├── hot-commodity.vue
│   │   │       │   ├── hot-products-list.vue
│   │   │       │   ├── product-sales.vue
│   │   │       │   ├── recent-transaction.vue
│   │   │       │   ├── sales-classification.vue
│   │   │       │   ├── sales-growth.vue
│   │   │       │   ├── sales-trend.vue
│   │   │       │   ├── total-order-volume.vue
│   │   │       │   ├── total-products.vue
│   │   │       │   └── transaction-list.vue
│   │   │       └── index.vue
│   │   ├── examples/
│   │   │   ├── forms/
│   │   │   │   ├── index.vue
│   │   │   │   └── search-bar.vue
│   │   │   ├── permission/
│   │   │   │   ├── button-auth/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── page-visibility/
│   │   │   │   │   └── index.vue
│   │   │   │   └── switch-role/
│   │   │   │       └── index.vue
│   │   │   ├── socket-chat/
│   │   │   │   └── index.vue
│   │   │   ├── tables/
│   │   │   │   ├── basic.vue
│   │   │   │   ├── index.vue
│   │   │   │   └── tree.vue
│   │   │   └── tabs/
│   │   │       └── index.vue
│   │   ├── exception/
│   │   │   ├── 403/
│   │   │   │   └── index.vue
│   │   │   ├── 404/
│   │   │   │   └── index.vue
│   │   │   └── 500/
│   │   │       └── index.vue
│   │   ├── index/
│   │   │   ├── index.vue
│   │   │   └── style.scss
│   │   ├── outside/
│   │   │   └── Iframe.vue
│   │   ├── result/
│   │   │   ├── fail/
│   │   │   │   └── index.vue
│   │   │   └── success/
│   │   │       └── index.vue
│   │   ├── safeguard/
│   │   │   └── server/
│   │   │       └── index.vue
│   │   ├── school/
│   │   │   ├── company-activities/
│   │   │   │   └── index.vue
│   │   │   ├── company-announcements/
│   │   │   │   └── index.vue
│   │   │   ├── dashboard/
│   │   │   │   └── index.vue
│   │   │   ├── databoard/
│   │   │   │   └── index.vue
│   │   │   ├── profile/
│   │   │   │   └── index.vue
│   │   │   ├── students/
│   │   │   │   └── index.vue
│   │   │   └── warnings/
│   │   │       └── index.vue
│   │   ├── showcase/
│   │   │   └── index.vue
│   │   ├── student/
│   │   │   ├── activities/
│   │   │   │   └── index.vue
│   │   │   ├── ai-decision/
│   │   │   │   └── index.vue
│   │   │   ├── ai-profile/
│   │   │   │   └── index.vue
│   │   │   ├── ai-resume/
│   │   │   │   └── index.vue
│   │   │   ├── announcements/
│   │   │   │   └── index.vue
│   │   │   ├── dashboard/
│   │   │   │   └── index.vue
│   │   │   ├── databoard/
│   │   │   │   └── index.vue
│   │   │   ├── interview-prep/
│   │   │   │   └── index.vue
│   │   │   ├── jobs/
│   │   │   │   └── index.vue
│   │   │   └── profile/
│   │   │       └── index.vue
│   │   ├── system/
│   │   │   ├── menu/
│   │   │   │   ├── modules/
│   │   │   │   │   └── menu-dialog.vue
│   │   │   │   └── index.vue
│   │   │   ├── nested/
│   │   │   │   ├── menu1/
│   │   │   │   │   └── index.vue
│   │   │   │   ├── menu2/
│   │   │   │   │   └── index.vue
│   │   │   │   └── menu3/
│   │   │   │       ├── menu3-2/
│   │   │   │       │   └── index.vue
│   │   │   │       └── index.vue
│   │   │   ├── role/
│   │   │   │   ├── modules/
│   │   │   │   │   ├── role-edit-dialog.vue
│   │   │   │   │   ├── role-permission-dialog.vue
│   │   │   │   │   └── role-search.vue
│   │   │   │   └── index.vue
│   │   │   ├── user/
│   │   │   │   ├── modules/
│   │   │   │   │   ├── user-dialog.vue
│   │   │   │   │   └── user-search.vue
│   │   │   │   └── index.vue
│   │   │   └── user-center/
│   │   │       └── index.vue
│   │   ├── template/
│   │   │   ├── banners/
│   │   │   │   └── index.vue
│   │   │   ├── calendar/
│   │   │   │   └── index.vue
│   │   │   ├── cards/
│   │   │   │   └── index.vue
│   │   │   ├── charts/
│   │   │   │   └── index.vue
│   │   │   ├── chat/
│   │   │   │   └── index.vue
│   │   │   ├── map/
│   │   │   │   └── index.vue
│   │   │   └── pricing/
│   │   │       └── index.vue
│   │   └── widgets/
│   │       ├── context-menu/
│   │       │   └── index.vue
│   │       ├── count-to/
│   │       │   └── index.vue
│   │       ├── drag/
│   │       │   └── index.vue
│   │       ├── excel/
│   │       │   └── index.vue
│   │       ├── fireworks/
│   │       │   └── index.vue
│   │       ├── icon/
│   │       │   └── index.vue
│   │       ├── image-crop/
│   │       │   └── index.vue
│   │       ├── qrcode/
│   │       │   └── index.vue
│   │       ├── text-scroll/
│   │       │   └── index.vue
│   │       ├── video/
│   │       │   └── index.vue
│   │       ├── wang-editor/
│   │       │   └── index.vue
│   │       └── watermark/
│   │           └── index.vue
│   ├── App.vue
│   ├── env.d.ts
│   └── main.ts
├── .auto-import.json
├── .prettierrc
├── .stylelintrc.cjs
├── CHANGELOG.md
├── CHANGELOG.zh-CN.md
├── commitlint.config.cjs
├── employment.db
├── eslint.config.mjs
├── index.html
├── LICENSE
├── luminous-stargazing-stream.md
├── package.json
├── README.md
├── README.zh-CN.md
├── showcase.html
├── test_output.csv
├── tsconfig.json
├── verify_import.csv
└── vite.config.ts
```

## Summary

- **Total directories**: 316
- **Total files**: 692
