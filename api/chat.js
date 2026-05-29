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
    const { message, history } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // 构建消息列表
    const messages = [];
    if (history && Array.isArray(history)) {
      history.forEach(item => {
        messages.push({ role: item.role, content: [{ type: 'text', text: item.content }] });
      });
    }
    messages.push({ role: 'user', content: [{ type: 'text', text: message }] });

    // 调用腾讯元器 API（流式）
    const response = await fetch('https://yuanqi.tencent.com/openapi/v1/agent/chat/completions', {
      method: 'POST',
      headers: {
        'X-Source': 'openapi',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${APPKEY}`
      },
      body: JSON.stringify({
        app_id: APPID,
        user_id: 'web_visitor_' + Date.now(),
        messages: messages,
        stream: false
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('Yuanqi API error:', response.status, errText);
      return res.status(response.status).json({ error: `API error: ${response.status}`, detail: errText });
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
      reply: reply || '抱歉，我暂时无法回答这个问题。',
      raw: data
    });

  } catch (err) {
    console.error('Server error:', err);
    return res.status(500).json({ error: 'Internal server error', detail: err.message });
  }
}
