// Глобальная переменная для CSRF токена
const csrf_token = "{{ generate_csrf() }}";

// Инициализация подсветки кода
hljs.configure({ languages: ['python', 'javascript', 'html', 'css', 'java', 'cpp', 'php', 'sql', 'json', 'bash'] });

// Функция для форматирования текста
function formatText(command, value = null) {
    document.getElementById('editor').focus();
    document.execCommand(command, false, value);
}

// Функция для вставки мультимедиа
function insertMedia(type) {
    const placeholder = `[${type.toUpperCase()}:введите_описание]`;
    const editor = document.getElementById('editor');
    const selection = window.getSelection();

    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        const placeholderNode = document.createTextNode(placeholder);
        range.deleteContents();
        range.insertNode(placeholderNode);

        // Установить курсор после плейсхолдера
        const newRange = document.createRange();
        newRange.setStartAfter(placeholderNode);
        newRange.collapse(true);
        selection.removeAllRanges();
        selection.addRange(newRange);
    }

    editor.focus();
}

// Инициализация панели форматирования
function initFormattingToolbar() {
    // Обработчики для кнопок форматирования
    $('#formattingToolbar button[data-format]').on('click', function() {
        const format = $(this).data('format');
        const value = $(this).data('value');
        formatText(format, value);
    });

    // Обработчики для вставки мультимедиа
    $('#formattingToolbar button[data-insert]').on('click', function() {
        const type = $(this).data('insert');
        insertMedia(type);
    });

    // Применить подсветку кода при изменении контента
    document.getElementById('editor').addEventListener('input', function() {
        this.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    });
}

// Преобразование HTML в Markdown-подобный формат
function htmlToMarkdown(html) {
    let markdown = html;

    // Заголовки
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');

    // Жирный текст
    markdown = markdown.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
    markdown = markdown.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');

    // Курсив
    markdown = markdown.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
    markdown = markdown.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');

    // Подчеркнутый
    markdown = markdown.replace(/<u[^>]*>(.*?)<\/u>/gi, '__$1__');

    // Зачеркнутый
    markdown = markdown.replace(/<s[^>]*>(.*?)<\/s>/gi, '~~$1~~');

    // Цитаты
    markdown = markdown.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gi, '> $1\n\n');

    // Списки
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gi, (match, content) => {
        const items = content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1');
        return items + '\n';
    });

    markdown = markdown.replace(/<ol[^>]*>(.*?)<\/ol>/gi, (match, content) => {
        let counter = 1;
        const items = content.replace(/<li[^>]*>(.*?)<\/li>/gi, (itemMatch, itemContent) => {
            return `${counter++}. ${itemContent}`;
        });
        return items + '\n';
    });

    // Блоки кода
    markdown = markdown.replace(/<pre><code[^>]*>(.*?)<\/code><\/pre>/gi, (match, content) => {
        return '```\n' + content + '\n```';
    });

    // Изображения
    markdown = markdown.replace(/<img[^>]*src="(.*?)"[^>]*alt="(.*?)"[^>]*>/gi, '![$2]($1)');

    // Видео
    markdown = markdown.replace(/<video[^>]*src="(.*?)"[^>]*>(.*?)<\/video>/gi, '[VIDEO]($1)');

    // Аудио
    markdown = markdown.replace(/<audio[^>]*src="(.*?)"[^>]*>(.*?)<\/audio>/gi, '[AUDIO]($1)');

    // Файлы
    markdown = markdown.replace(/<a[^>]*href="(.*?)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');

    // Удаление остальных тегов
    markdown = markdown.replace(/<[^>]*>/g, '');

    // Очистка лишних пробелов
    markdown = markdown.replace(/\n\s*\n/g, '\n\n').trim();

    return markdown;
}

// Преобразование Markdown в HTML
function markdownToHtml(markdown) {
    let html = markdown;

    // Заголовки
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');

    // Жирный текст
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

    // Курсив
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

    // Подчеркнутый
    html = html.replace(/__(.*?)__/gim, '<u>$1</u>');

    // Зачеркнутый
    html = html.replace(/~~(.*?)~~/gim, '<s>$1</s>');

    // Цитаты
    html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');

    // Маркированные списки
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');

    // Нумерованные списки
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gim, '<ol>$1</ol>');

    // Блоки кода
    html = html.replace(/```([a-z]*)\n([\s\S]*?)```/gim, (match, lang, code) => {
        const highlighted = hljs.highlightAuto(code, lang ? [lang] : null).value;
        return `<pre><code class="hljs ${lang || ''}">${highlighted}</code></pre>`;
    });

    // Изображения
    html = html.replace(/!\[(.*?)\]\((.*?)\)/gim, '<img src="$2" alt="$1" class="img-fluid">');

    // Видео
    html = html.replace(/\[VIDEO\]\((.*?)\)/gim, '<video controls class="w-100"><source src="$1" type="video/mp4"></video>');

    // Аудио
    html = html.replace(/\[AUDIO\]\((.*?)\)/gim, '<audio controls class="w-100"><source src="$1" type="audio/mpeg"></audio>');

    // Ссылки
    html = html.replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank">$1</a>');

    // Переносы строк
    html = html.replace(/\n/g, '<br>');

    // Очистка HTML
    html = DOMPurify.sanitize(html);

    return html;
}

$(document).ready(function() {
    // Переменная для хранения модального окна
    const noteModal = new bootstrap.Modal(document.getElementById('noteModal'));

    // Открытие заметки в модальном окне
    $('.note-card').on('click', function(e) {
        // Проверяем, не кликнули ли на кнопку удаления
        if ($(e.target).closest('.delete-note').length === 0) {
            const noteId = $(this).data('id');
            openNoteForEditing(noteId);
        }
    });

    // Обработчик для кнопок удаления
    $('.delete-note').on('click', function(e) {
        e.stopPropagation();
        const noteId = $(this).data('id');
        const cardElement = $(this).closest('.col');
        deleteNote(noteId, cardElement);
    });

    // Сохранение заметки
    $('#saveNoteBtn').on('click', saveNote);

    // Инициализация панели форматирования
    initFormattingToolbar();

    // Конвертация Markdown при отображении заметок
    $('.note-content').each(function() {
        const markdown = $(this).html();
        const html = markdownToHtml(markdown);
        $(this).html(html);
    });

    // Обработчик загрузки файлов
    $('#newAttachments').on('change', function(e) {
        const files = e.target.files;
        if (files.length === 0) return;

        let previewHtml = '<div class="mb-3"><strong>Новые вложения:</strong><div class="d-flex flex-wrap gap-2 mt-2">';

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const objectUrl = URL.createObjectURL(file);

            if (file.type.startsWith('image/')) {
                previewHtml += `<img src="${objectUrl}" class="img-thumbnail" style="max-width: 100px;">`;
            } else if (file.type.startsWith('video/')) {
                previewHtml += `
                    <div class="border p-2">
                        <video controls width="150" height="100">
                            <source src="${objectUrl}" type="${file.type}">
                        </video>
                        <small class="d-block">${file.name}</small>
                    </div>
                `;
            } else if (file.type.startsWith('audio/')) {
                previewHtml += `
                    <div class="border p-2">
                        <audio controls>
                            <source src="${objectUrl}" type="${file.type}">
                        </audio>
                        <small class="d-block">${file.name}</small>
                    </div>
                `;
            } else {
                previewHtml += `
                    <div class="border p-2 text-center">
                        <i class="bi bi-file-earmark fs-1"></i>
                        <small class="d-block">${file.name}</small>
                    </div>
                `;
            }
        }

        previewHtml += '</div></div>';
        $('#attachmentsPreview').html(previewHtml);
    });
});

function openNoteForEditing(noteId) {
    // Показать индикатор загрузки
    $('#loadingIndicator').removeClass('d-none');
    $('#noteFormContainer').addClass('d-none');
    $('#errorContainer').addClass('d-none').empty();

    // Открыть модальное окно
    const noteModal = new bootstrap.Modal(document.getElementById('noteModal'));
    noteModal.show();

    // Загрузить данные заметки
    fetch(`/api/note/${noteId}`)
        .then(response => {
            if (!response.ok) throw new Error('Заметка не найдена');
            return response.json();
        })
        .then(note => {
            // Заполнить форму данными
            $('#note_id').val(note._id);
            $('#title').val(note.title);
            $('#category').val(note.category || '');

            // Установка тегов
            const tagsSelect = $('#tags');
            tagsSelect.val(note.tags);

            // Даты
            if (note.created_at) {
                const createdDate = new Date(note.created_at);
                $('#createdAt').text(createdDate.toLocaleString('ru-RU'));
            }

            if (note.updated_at) {
                const updatedDate = new Date(note.updated_at);
                $('#updatedAt').text(updatedDate.toLocaleString('ru-RU'));
            }

            // Отображение контента в редакторе
            const editor = document.getElementById('editor');
            editor.innerHTML = markdownToHtml(note.content);

            // Применить подсветку кода
            editor.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });

            // Отображение существующих вложений
            if (note.attachments && note.attachments.length > 0) {
                let attachmentsHtml = '<div class="mb-3"><strong>Текущие вложения:</strong><div class="d-flex flex-wrap gap-2 mt-2">';

                note.attachments.forEach(attachment => {
                    if (attachment.type === 'image') {
                        attachmentsHtml += `<img src="${attachment.url}" class="img-thumbnail" style="max-width: 100px;">`;
                    } else if (attachment.type === 'video') {
                        attachmentsHtml += `
                            <div class="border p-2">
                                <video controls width="150" height="100">
                                    <source src="${attachment.url}" type="video/mp4">
                                </video>
                                <small class="d-block">${attachment.name}</small>
                            </div>
                        `;
                    } else if (attachment.type === 'audio') {
                        attachmentsHtml += `
                            <div class="border p-2">
                                <audio controls>
                                    <source src="${attachment.url}" type="audio/mpeg">
                                </audio>
                                <small class="d-block">${attachment.name}</small>
                            </div>
                        `;
                    } else {
                        attachmentsHtml += `
                            <div class="border p-2 text-center">
                                <i class="bi bi-file-earmark fs-1"></i>
                                <small class="d-block">${attachment.name}</small>
                            </div>
                        `;
                    }
                });

                attachmentsHtml += '</div></div>';
                $('#attachmentsPreview').html(attachmentsHtml);
            }

            // Показать форму
            $('#loadingIndicator').addClass('d-none');
            $('#noteFormContainer').removeClass('d-none');
        })
        .catch(error => {
            console.error('Ошибка загрузки заметки:', error);

            // Показать сообщение об ошибке
            $('#loadingIndicator').addClass('d-none');
            $('#errorContainer')
                .removeClass('d-none')
                .html(`<strong>Ошибка!</strong> Не удалось загрузить заметку: ${error.message}`);
        });
}

function saveNote() {
    const noteId = $('#note_id').val();
    const title = $('#title').val().trim();
    const editorContent = document.getElementById('editor').innerHTML;

    // Конвертируем HTML в Markdown для хранения
    const markdownContent = htmlToMarkdown(editorContent);

    // Простая валидация
    if (!title) {
        alert('Введите заголовок заметки');
        return;
    }

    if (!markdownContent) {
        alert('Введите содержание заметки');
        return;
    }

    // Установить значение скрытого поля
    $('#content').val(markdownContent);

    // Собираем данные формы
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', markdownContent);
    formData.append('tags', JSON.stringify($('#tags').val() || []));
    formData.append('category', $('#category').val().trim() || '');
    formData.append('note_id', noteId);

    // Добавляем новые вложения
    const attachments = document.getElementById('newAttachments').files;
    for (let i = 0; i < attachments.length; i++) {
        formData.append('attachments', attachments[i]);
    }

    // Показать индикатор сохранения
    const saveBtn = $('#saveNoteBtn');
    const originalBtnHtml = saveBtn.html();
    saveBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Сохранение...');

    fetch(`/note/${noteId}`, {
        method: 'PUT',
        headers: {
            'X-CSRF-Token': csrf_token
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сохранения');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Закрыть модальное окно
            const noteModal = bootstrap.Modal.getInstance(document.getElementById('noteModal'));
            noteModal.hide();

            // Обновить интерфейс
            setTimeout(() => {
                location.reload();
            }, 300);
        } else {
            throw new Error(data.message || 'Ошибка при сохранении');
        }
    })
    .catch(error => {
        console.error('Ошибка сохранения заметки:', error);
        alert('Ошибка при сохранении: ' + error.message);
    })
    .finally(() => {
        saveBtn.prop('disabled', false).html(originalBtnHtml);
    });
}

function deleteNote(noteId, cardElement) {
    if (!confirm('Вы уверены, что хотите удалить эту заметку? Это действие нельзя отменить.')) {
        return;
    }

    // Показать индикатор удаления
    const deleteBtn = $(`.delete-note[data-id="${noteId}"]`);
    const originalBtnHtml = deleteBtn.html();
    deleteBtn.html('<span class="spinner-border spinner-border-sm"></span>');
    deleteBtn.prop('disabled', true);

    fetch(`/note/${noteId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRF-Token': csrf_token
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка удаления');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Анимация удаления карточки
            cardElement.fadeOut(300, function() {
                $(this).remove();

                // Проверить, остались ли заметки
                if ($('#notes-container .col').length === 0) {
                    $('#notes-container').html(`
                        <div class="col-12">
                            <div class="alert alert-info">У вас пока нет заметок</div>
                        </div>
                    `);
                }
            });
        } else {
            throw new Error(data.message || 'Ошибка при удалении');
        }
    })
    .catch(error => {
        console.error('Ошибка удаления заметки:', error);
        alert('Ошибка при удалении: ' + error.message);
    })
    .finally(() => {
        deleteBtn.html(originalBtnHtml);
        deleteBtn.prop('disabled', false);
    });
}