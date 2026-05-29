// Vercel Serverless Function - 腾讯元器 API 代理
export default async function handler(req, res) {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const APPKEY = process.env.YUANQI_APPKEY || 'IXr04nzbkZowxXZsy3YrflhUg9SNsuvk';
  const APPID = process.env.YUANQI_APPID || '2060004427884063808';

  try {
    // 兼容处理 body 解析
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch(e) { body = {}; }
    }
    if (!body) body = {};

    const message = body.message;
    const history = body.history;

    if (!message) {
      return res.status(400).json({ error: 'Message is required', receivedBody: JSON.stringify(body).substring(0, 100) });
    }

    // 构建消息列表
    const messages = [];
    if (history && Array.isArray(history)) {
      history.forEach(item => {
        messages.push({ role: item.role, content: item.content });
      });
    }
    messages.push({ role: 'user', content: message });

    // 调用腾讯元器 API
    const requestBody = {
      app_id: APPID,
      user_id: 'web_user_001',
      messages: messages,
      stream: false
    };

    const response = await fetch('https://yuanqi.tencent.com/openapi/v1/agent/chat/completions', {
      method: 'POST',
      headers: {
        'X-Source': 'openapi',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${APPKEY}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(200).json({ reply: '', error: `API返回${response.status}`, detail: errText.substring(0, 300), sentBody: JSON.stringify(requestBody).substring(0, 300) });
    }

    const data = await response.json();

    // 提取回复内容
    let reply = '';
    if (data.choices && data.choices.length > 0) {
      const content = data.choices[0].message?.content;
      if (typeof content === 'string') {
        reply = content;
      } else if (Array.isArray(content)) {
        reply = content.map(c => c.text || '').join('');
      }
    }

    return res.status(200).json({
      reply: reply || '',
      debug: !reply ? JSON.stringify(data).substring(0, 500) : undefined
    });

  } catch (err) {
    return res.status(200).json({ reply: '', error: 'Server error: ' + err.message });
  }
}
