import { CodeEditor } from '@jupyterlab/codeeditor';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

import {timeout, handleFetch, HEADER_COMMON, API_URL} from "./apiUtils";
import { _debugVarInfo, CompResult, AnalyzeCodeResp } from "../interfaces";
import { IColLvInfo, IRowLvInfo, ITableLvInfo } from '../sidePanel/interface';

// 服务发现：优先使用JupyterLab集成服务，回退到独立服务器
async function getApiUrl(): Promise<string> {
  // 尝试JupyterLab集成服务
  try {
    const settings = ServerConnection.makeSettings();
    const jupyterUrl = URLExt.join(settings.baseUrl, 'xavier');
    
    // 健康检查
    const healthResponse = await fetch(`${jupyterUrl}/health`, {
      method: 'GET',
      headers: HEADER_COMMON
    });
    
    if (healthResponse.ok) {
      console.log('🎯 Using JupyterLab integrated Xavier service');
      return jupyterUrl;
    }
  } catch (error) {
    // JupyterLab服务不可用，继续尝试独立服务器
  }
  
  // 回退到独立服务器
  try {
    const standaloneUrl = 'http://localhost:5000';
    const healthResponse = await fetch(`${standaloneUrl}/health`, {
      method: 'GET',
      headers: HEADER_COMMON
    });
    
    if (healthResponse.ok) {
      console.log('🎯 Using standalone Xavier service');
      return standaloneUrl;
    }
  } catch (error) {
    // 独立服务器也不可用
  }
  
  throw new Error('Xavier service not available. Please ensure either JupyterLab extension is loaded or standalone server is running.');
}

//previousCode2D, token, nbApi.dfList, nbApi.allDfInfo
export async function completeQuery(previousCode2D: string[][], token: CodeEditor.IToken, tableLvInfo: ITableLvInfo, rowLvInfo: IRowLvInfo, colLvInfo: IColLvInfo): Promise<CompResult> {
  try {
    const apiUrl = await getApiUrl();
    
    const resp = await timeout(400000000, fetch(`${apiUrl}/complete`, {
      method: 'POST',
      headers: HEADER_COMMON,
      body: JSON.stringify({
        'previousCode2D': previousCode2D,
        'token': {
          ...token,
          "type": token.type === undefined ? null : token.type,
        },
        'tableLvInfo': tableLvInfo,
        'colLvInfo': colLvInfo,
        'rowLvInfo': rowLvInfo,
      })
    }));
    const j = await handleFetch(resp) as CompResult;
    return j;
  } catch (e) {
    console.log("[completeQuery] Error:", e);
    return {
      tokenList: [],
      analyzeResp: null,
    };
  }
};

export async function analyzeCodeQuery(previousCode2D: string[][], dfList: _debugVarInfo[]) {
  const resp = await timeout(400000000, fetch(API_URL + '/analyze_code', {
    method: 'POST',
    headers: HEADER_COMMON,
    body: JSON.stringify({
      'code': previousCode2D,
      'activeDfs': dfList
    })
  }));
  const j = await handleFetch(resp);
  return j as AnalyzeCodeResp;
};