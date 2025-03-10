document.addEventListener("DOMContentLoaded", () => {
    const API_HEADERS = { 'Content-Type': 'application/json' };
    const FETCH_ERROR_MSG = "データ取得に失敗しました: ";
    const SERVER_ERROR_MSG = "サーバーエラーが発生しました: ";
    const NETWORK_ERROR_MSG = "ネットワークエラー: ";
    const MAX_CHECKED_LIMIT = 5;

    // ① ロード時の通知設定取得と反映
    const fetchAndSetToggleValue = async (checkbox) => {
        const orderCode = checkbox.id.replace('toggle-', '');
        try {
            const response = await fetch("/api/get_notification_setting", {
                method: 'POST',
                headers: API_HEADERS,
                body: JSON.stringify({ order_code: orderCode })
            });
            if (!response.ok) {
                throw new Error(`${FETCH_ERROR_MSG}${response.statusText}`);
            }
            const data = await response.json();
            if (data.success) {
                checkbox.checked = data.toggleValue; // true または false
            } else {
                console.error("通知状態の取得に失敗しました: ", data);
            }
        } catch (error) {
            console.error("初期化エラー: ", error.message);
        }
    };

    // ② チェックボックス変更時の通知設定送信
    const sendToggleUpdate = async (checkbox) => {
        const isChecked = checkbox.checked;
        const orderCode = checkbox.id.replace('toggle-', '');
        try {
            const response = await fetch('/api/update_notification_setting', {
                method: 'POST',
                headers: API_HEADERS,
                body: JSON.stringify({
                    order_code: orderCode,
                    is_checked: isChecked
                })
            });
            if (!response.ok) {
                console.error(`${SERVER_ERROR_MSG}${response.statusText}`);
                return;
            }
            const data = await response.json();
            console.log("サーバーからのレスポンス:", data);
        } catch (error) {
            console.error(`${NETWORK_ERROR_MSG}${error.message}`);
        }
    };

    //現在チェックされているチェックボックスるの数をカウント
    const countChecked = () => {
        return [...document.querySelectorAll('.toggleButton__checkbox')]
        .filter(checkbox => checkbox.checked).length;
    };

    //チェックボックス変更時の確認ロジック
    const handleCheckboxChange = (checkbox) => {
        const checkedCount = countChecked();

        if (checkedCount > MAX_CHECKED_LIMIT){
            alert(`LINE通知は最大${MAX_CHECKED_LIMIT}個までです。`);
            checkbox.checked = false;
            return;
        }

        //制約がない場合
        sendToggleUpdate(checkbox);
    };

    // 全てのチェックボックスに対する操作設定
    document.querySelectorAll('.toggleButton__checkbox').forEach(async (checkbox) => {
        // 初期化で通知設定を取得して反映
        await fetchAndSetToggleValue(checkbox);

        // 変更時に通知設定を送信
        checkbox.addEventListener('change', () => handleCheckboxChange(checkbox));
    });
});