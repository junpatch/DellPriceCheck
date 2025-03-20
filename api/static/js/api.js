document.addEventListener("DOMContentLoaded", async () => {
  const productNameSelect = document.getElementById("productNameSelect");
  const productModelSelect = document.getElementById("productModelSelect");
  const isLocal = window.location.hostname === "localhost" || window.location.hostname.startsWith("127.");
  const BASE_URL = isLocal ? "" : "/dev";

  // 共通の option 要素作成関数
  function createOptionElement(value, textContent) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = textContent;
    return option;
  }

  productNameSelect.addEventListener("change", async (event) => {
    const selectedName = event.target.value;

    // 初期状態のオプションを設定
    productModelSelect.innerHTML = "";
    productModelSelect.appendChild(createOptionElement("", "--model名を選択--"));
    productModelSelect.disabled = true;

    if (!selectedName) return;

    try {
      const response = await fetch(`${BASE_URL}/api/get_model/${encodeURIComponent(selectedName)}`);
      const modelList = await response.json();

      if (modelList.length > 0) {
        modelList.forEach((item) => {
          productModelSelect.appendChild(createOptionElement(item.model, item.model));
        });
        productModelSelect.disabled = false;
      }
    } catch (error) {
      console.error("モデルリストの取得に失敗しました:", error);
    }
  });

  // チャートの描画
  const productLink = document.getElementById("productLink")
  const productSelectionForm = document.getElementById("productSelectionForm");
  const priceTrendCanvas = document.getElementById("priceTrendChart");

  if (!priceTrendCanvas) {
    console.error("priceTrendChart 要素が見つかりません。");
    return;
  }

  const ctx = priceTrendCanvas.getContext("2d");
  let chartInstance = null;

  productSelectionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    // 前回のチャートを破棄
    if (chartInstance) chartInstance.destroy();

    const name = productNameSelect.value;
    const model = productModelSelect.value;

    try {
      const response = await fetch(`${BASE_URL}/api/get_price_trend/${encodeURIComponent(name)}/${encodeURIComponent(model)}`);
      const data = await response.json();

      if (data.prices?.length > 0) {
        const labels = data.prices.map((entry) => entry.date); // 日付データ
        const prices = data.prices.map((entry) => entry.price); // 価格データ

        chartInstance = new Chart(ctx, {
          type: "line",
          data: {
            labels,
            datasets: [
              {
                label: "価格推移",
                data: prices,
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              title: { display: true, text: `${name} - ${model}` },
              legend: { display: true, position: "top" },
              tooltip: { enabled: true },
            },
            scales: {
              x: {
                type: "time",
                time: { unit: "day", tooltipFormat: "YYYY-MM-DD" },
                title: { display: true, text: "日付" },
              },
            },
          },
        });

        productLink.innerHTML = `<p><a href=${data.url}>＞リンク</a><p>`

      } else {
        trendOutputDiv.innerHTML = "<p>価格推移のデータがありません。</p>";
      }
    } catch (error) {
      console.error("価格データの取得に失敗しました:", error);
      trendOutputDiv.innerHTML = "<p class='error'>価格推移を取得できませんでした。</p>";
    }
  });
  //グラフ描画ここまで

  // 価格データ取得（いずれ消す）
  const btnGetLatest = document.getElementById("getLatest");

  btnGetLatest.addEventListener("click", async (event) => {
    event.preventDefault(); // デフォルト動作を防ぐ（URL遷移しない）
    const url = `${BASE_URL}/api/check_price`;
    const data = await requestScraping(url);
  });

  // 通知テスト（いずれ消す）
  const btnNotificationTest = document.getElementById("notificationTest");

  btnNotificationTest.addEventListener("click", async (event) => {
    event.preventDefault(); // デフォルト動作を防ぐ（URL遷移しない）
    const url = `${BASE_URL}/api/notification_test`;
    const data = await requestScraping(url);

  });
  
  // ✅ 再利用可能な fetch 関数
  async function requestScraping(url) {
    let data = null;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`fetchで正しいレスポンスが返ってきません (${url}): ${response.status} - ${response.statusText}`);
      }
      data = await response.json();
    } catch (error) {
      console.error(`fetchエラー (${url})::`, error.message);
      alert(`fetchエラー (${url}):: ${error.message}`);
      return null;  // エラー時は null を返す
    }

    if (data.taskArn) {
      alert("スクレイピングを開始しました！");
      checkScrapingStatus(data.taskArn)
    } else {
      console.error(`スクレイピングを開始できませんでした data:${data}, taskArn:${taskArn}`);
      alert("スクレイピングを開始できませんでした");
    }

    return data

  }

  // ✅ 定期的にスクレイピングの結果を取得する関数
  async function checkScrapingStatus(taskArn) {
    const checkInterval = 10000; // 10秒ごとに確認
    const maxRetries = 60; // 最大 60回 (10分)
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;
      try {
        // 🎯 最新のスクレイピング結果を取得
        const taskArn_encoded = encodeURIComponent(taskArn);  // taskArnをURLエンコードする
        const response = await fetch(`${BASE_URL}/api/get_scraping_status/${taskArn_encoded}`);
        if (!response.ok) {
          clearInterval(interval);
          const errorBody = await response.text(); // レスポンスボディを取得
          console.error(`レスポンス異常: ${response.status} - ${response.statusText}`, errorBody);
          throw new Error(`レスポンス異常: ${response.status} - ${response.statusText}`);
        }
        const result = await response.json();

        if (result.status === "STOPPED" && result.stopReason === "Essential container in task exited"){
          clearInterval(interval);
          alert(`スクレイピング完了！`);
        } else if (result.status === "STOPPED") {
          clearInterval(interval);
          alert(`スクレイピング異常終了: ${result.stopReason}`);
        } else if (attempts >= maxRetries) {
          clearInterval(interval);
          alert("タイムアウトしました。");
        } else if (result.status ==="UNKNOWN") {
          clearInterval(interval);
          alert(`AWSタスクが見つかりません。ステータス不明。`)
        }

      } catch (error) {
        clearInterval(interval);
        console.error("fetchエラー(get_scraping_status):", error);
        alert(`fetchエラー(get_scraping_status): ${error.message}`);
      }
    }, checkInterval);
  }

});