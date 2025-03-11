document.addEventListener("DOMContentLoaded", () => {
    const API_HEADERS = { 'Content-Type': 'application/json' };
    const FETCH_ERROR_MSG = "データ取得に失敗しました: ";
    const SERVER_ERROR_MSG = "サーバーエラーが発生しました: ";
    const NETWORK_ERROR_MSG = "ネットワークエラー: ";
    const MAX_CHECKED_LIMIT = 5;
    const BASE_URL = window.location.hostname === "localhost"
        ? ""  // ローカル環境ではそのまま相対パス
        : "/dev";  // Lambda の場合は /dev 付き

    // ① ロード時の通知設定取得と反映
    const fetchAndSetALLToggleValues = async() => {
        try {
            const response = await fetch(`${BASE_URL}/api/get_notification_setting`);
            const data = await response.json();
            console.log("Response Data:", data); // レスポンスの内容を確認
            
            if (!response.ok) {
                throw new Error(`${FETCH_ERROR_MSG}${response.statusText}`);
            }
        
            if (data.success) {
                for (orderCode in data.toggleValues) {
                    const checkbox = document.querySelector(`#toggle-${orderCode}`);
                    if (checkbox) {
                        checkbox.checked = data.toggleValues[orderCode]; // true または false
                    }
                }
            } else {
                console.error("サーバー側でDBの取得に失敗しました: ", data);
            }
        } catch (error) {
            console.error("Line通知設定初期化エラー: ", error.message);
        }

    };

    // ② チェックボックス変更時の通知設定送信
    const sendToggleUpdate = async (checkbox) => {
        const isChecked = checkbox.checked;
        const orderCode = checkbox.id.replace('toggle-', '');
        try {
            const response = await fetch(`${BASE_URL}/api/update_notification_setting`, {
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

    //現在チェックされているチェックボックスの数をカウント
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

    // チェックボックスクリック時に変更情報を送信
    document.querySelectorAll('.toggleButton__checkbox').forEach(async (checkbox) => {
        checkbox.addEventListener('change', () => handleCheckboxChange(checkbox));
    });

    // ページロード時に全てのチェックボックスの通知設定を一度だけ取得して反映
    fetchAndSetALLToggleValues();

});