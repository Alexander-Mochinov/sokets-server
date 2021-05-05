function limitInput(k, obj) {
    switch (k) {
        case 'ru':
            obj.value = obj.value.replace(/[^а-яА-ЯёЁ0-9 -]/ig, '');
            break;
        case 'en':
            obj.value = obj.value.replace(/[^a-zA-Z0-9 -]/ig, '');
            break;
    }
}