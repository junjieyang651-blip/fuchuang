// Cloudflare Worker - 腾讯元器 API 代理
// 部署到 Cloudflare Workers 后，国内可直接访问

const APPKEY = 'IXr04nzbkZowxXZsy3YrflhUg9SNsuvk';
const APPID = '2060004427884063808';

export default {
  async fetch(request) {
    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        }
      });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }

    try {
      const body = await request.json();
      const message = body.message;
      const history = body.history;

      if (!message) {
        return jsonResponse({ error: 'Message is required' }, 400);
      }

      // 构建消息列表
      const messages = [];
      if (history && Array.isArray(history)) {
        history.forEach(item => {
          messages.push({ role: item.role, content: [{ type: 'text', text: item.content }] });
        });
      }
      messages.push({ role: 'user', content: [{ type: 'text', text: message }] });

      const requestBody = {
        assistant_id: APPID,
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

      const data = await response.json();

      let reply = '';
      if (data.choices && data.choices.length > 0) {
        const content = data.choices[0].message?.content;
        if (typeof content === 'string') {
          reply = content;
        } else if (Array.isArray(content)) {
          reply = content.map(c => c.text || '').join('');
        }
      }

      return jsonResponse({ reply: reply || '' });

    } catch (err) {
      return jsonResponse({ reply: '', error: 'Server error: ' + err.message });
    }
  }
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  });
}
