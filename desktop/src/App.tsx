import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { ask, message, open } from '@tauri-apps/plugin-dialog';
import { fetch as tauriFetch } from '@tauri-apps/plugin-http';
import { openUrl } from '@tauri-apps/plugin-opener';
import { AuthError, OfflineError, TrackerApi } from './lib/api';
import { legacyToTasks, parseLegacyDay } from './lib/legacy';
import {
  activeTask, addTasks, compact, pendingTasks, recordWithoutStart, startTask, stopTask,
} from './lib/queue';
import { loadSettings, loadState, readLegacyDir, saveSettings, saveState } from './lib/storage';
import { syncPending } from './lib/sync';
import { formatElapsed, fromStamp, toStamp } from './lib/time';
import {
  DEFAULT_SETTINGS, EMPTY_STATE, type Category, type LocalState, type Settings,
} from './lib/types';
import {
  BackIcon, ChartIcon, CloudCheckIcon, ExternalIcon, ImportIcon, MenuIcon, PlayIcon, RefreshIcon,
  SettingsIcon, StopIcon,
} from './icons';

type View = 'main' | 'menu' | 'settings';
const NEW_CATEGORY = 'new';
const pluralTasks = (n: number) => `${n} ${n % 10 === 1 && n % 100 !== 11 ? 'запись' : 'записи'}`;
const CHECK_TOKEN = 'Проверь токен в настройках';

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [state, setStateValue] = useState<LocalState>(EMPTY_STATE);
  const stateRef = useRef<LocalState>(EMPTY_STATE);
  const saveChain = useRef<Promise<unknown>>(Promise.resolve());
  const [view, setView] = useState<View>('main');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [newCategory, setNewCategory] = useState<string | null>(null);
  const [categoryError, setCategoryError] = useState('');
  const [now, setNow] = useState(() => Date.now());
  // The server refused the token (or there is none): sending waits until it is fixed.
  const [authFailed, setAuthFailedValue] = useState(false);
  const authFailedRef = useRef(false);
  const setAuthFailed = useCallback((value: boolean) => {
    authFailedRef.current = value;
    setAuthFailedValue(value);
  }, []);

  // The window follows its content: compact for the timer, taller for settings and menu.
  const appRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = appRef.current;
    if (!node) return;
    // Requested size minus the content height it produced (the title bar on some platforms).
    let offset = 0;
    let requested: number | null = null;
    const contentHeight = () => Math.ceil(node.getBoundingClientRect().height);
    const fit = () => {
      const height = contentHeight();
      if (Math.abs(window.innerHeight - height) <= 1) return;
      requested = height + offset;
      invoke('fit_window', { width: window.innerWidth, height: requested }).catch(console.error);
    };
    const onResize = () => {
      if (requested === null) return;
      offset = requested - window.innerHeight;
      requested = null;
      fit();
    };
    const observer = new ResizeObserver(fit);
    observer.observe(node);
    window.addEventListener('resize', onResize);
    return () => {
      observer.disconnect();
      window.removeEventListener('resize', onResize);
    };
  }, [loaded]);

  const api = useMemo(
    () => new TrackerApi(settings.serverUrl, tauriFetch, settings.token),
    [settings.serverUrl, settings.token]);
  // A sync already in flight picks up a changed address or token on its next round.
  const apiRef = useRef(api);
  apiRef.current = api;

  // Every change is written to disk in order before anything is sent to the server.
  const setState = useCallback((next: LocalState) => {
    stateRef.current = next;
    setStateValue(next);
    saveChain.current = saveChain.current.then(() => saveState(next)).catch(console.error);
  }, []);

  const syncing = useRef(false);
  const syncAgain = useRef(false);
  const runSync = useCallback(async (retryRejected = false) => {
    if (syncing.current) {
      syncAgain.current = true;
      return;
    }
    syncing.current = true;
    try {
      do {
        syncAgain.current = false;
        const current = apiRef.current;
        const result = await syncPending(current, () => stateRef.current, setState, retryRejected);
        if (result.unauthorized) {
          setAuthFailed(true);
          continue;
        }
        if (result.offline) continue;
        let categories: Category[] | null = null;
        try {
          categories = await current.categories();
        } catch (error) {
          if (error instanceof AuthError) {
            setAuthFailed(true);
            continue;
          }
        }
        setAuthFailed(false);
        setState(compact({
          ...stateRef.current,
          lastSyncAt: toStamp(new Date()),
          categories: categories ?? stateRef.current.categories,
        }));
      } while (syncAgain.current);
    } finally {
      syncing.current = false;
    }
  }, [setState, setAuthFailed]);

  useEffect(() => {
    void (async () => {
      const [savedSettings, savedState] = await Promise.all([loadSettings(), loadState()]);
      stateRef.current = savedState;
      setStateValue(savedState);
      setSettings(savedSettings);
      const running = activeTask(savedState);
      if (running) {
        setDescription(running.description);
        setCategoryId(running.categoryId);
      }
      if (!savedSettings.serverUrl || !savedSettings.token) setView('settings');
      setLoaded(true);
    })();
  }, []);

  // On start and whenever the server address changes: pick up a task started on another
  // computer, then send what is queued.
  useEffect(() => {
    if (!loaded || !settings.serverUrl) return;
    void (async () => {
      if (!activeTask(stateRef.current)) {
        const remote = await api.activeTask().catch(() => null);
        if (remote?.client_id && remote.start_timestamp && !activeTask(stateRef.current)) {
          setState(addTasks(stateRef.current, [{
            clientId: remote.client_id, description: remote.description,
            categoryId: remote.category_id, start: remote.start_timestamp, finish: null,
            synced: true,
          }]));
          setDescription(remote.description);
          setCategoryId(remote.category_id);
        }
      }
      await runSync();
    })();
  }, [loaded, settings.serverUrl, api, runSync, setState]);

  useEffect(() => {
    if (!loaded || settings.syncIntervalMinutes <= 0) return;
    const timer = setInterval(() => void runSync(), settings.syncIntervalMinutes * 60_000);
    return () => clearInterval(timer);
  }, [loaded, settings.syncIntervalMinutes, runSync]);

  const running = activeTask(state);
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [running]);

  const pending = pendingTasks(state).length;
  const needsToken = authFailed || !settings.token;
  const unsent = pending > 0 ? `${pluralTasks(pending)} не отправлено` : '';
  const dotTitle = needsToken ? [unsent, CHECK_TOKEN].filter(Boolean).join('. ') : unsent;
  const input = { description: description.trim(), categoryId };
  const canStart = !running && input.description.length > 0;

  function onStart() {
    if (!canStart) return;
    setState(startTask(stateRef.current, input, toStamp(new Date()), crypto.randomUUID()));
    setNow(Date.now());
    void runSync();
  }

  function onStop() {
    setState(stopTask(stateRef.current, toStamp(new Date())));
    setDescription('');
    void runSync();
  }

  function onRecordWithoutStart() {
    if (!canStart) return;
    setState(recordWithoutStart(
      stateRef.current, input, toStamp(new Date()), crypto.randomUUID()));
    setDescription('');
    void runSync();
  }

  async function onCreateCategory() {
    const name = (newCategory ?? '').trim();
    if (!name) return;
    try {
      const created = await api.createCategory(name);
      setState({ ...stateRef.current, categories: [...stateRef.current.categories, created] });
      setCategoryId(created.id);
      setNewCategory(null);
      setCategoryError('');
    } catch (error) {
      if (error instanceof AuthError) setAuthFailed(true);
      setCategoryError(error instanceof AuthError ? CHECK_TOKEN
        : error instanceof OfflineError ? 'Нет связи с сервером' : 'Не удалось создать категорию');
    }
  }

  async function onImportLegacy() {
    setView('main');
    const folder = await open({ directory: true, title: 'Папка со старыми JSON' });
    if (typeof folder !== 'string') return;
    const files = await readLegacyDir(folder);
    const records = files.flatMap(([name, text]) => parseLegacyDay(name, text));
    if (records.length === 0) {
      await message('В этой папке нет записей старой версии.', { title: 'Импорт' });
      return;
    }
    const days = records.map((record) => record.date).sort();
    const confirmed = await ask(
      `Найдено ${pluralTasks(records.length)} за ${days[0]} — ${days[days.length - 1]}. ` +
      'Отправить на сервер? Повторный импорт не создаст дублей.',
      { title: 'Импорт', okLabel: 'Отправить', cancelLabel: 'Отмена' });
    if (!confirmed) return;
    try {
      const categories = await api.categories();
      const ids = new Map(categories.map((c) => [c.name.toLowerCase(), c.id]));
      for (const name of new Set(records.map((r) => r.category).filter(Boolean))) {
        if (!ids.has(name.toLowerCase())) {
          const created = await api.createCategory(name.slice(0, 50));
          ids.set(name.toLowerCase(), created.id);
        }
      }
      setState(addTasks(stateRef.current, await legacyToTasks(records, ids)));
      await runSync(true);
      const left = pendingTasks(stateRef.current).length;
      await message(left
        ? `Часть записей не отправлена (${left}). Они остались в очереди.` +
          (authFailedRef.current ? ` ${CHECK_TOKEN}.` : '')
        : 'Старые записи отправлены.', { title: 'Импорт' });
    } catch (error) {
      if (error instanceof AuthError) setAuthFailed(true);
      await message(error instanceof AuthError ? `Импорт не удался. ${CHECK_TOKEN}.`
        : error instanceof OfflineError ? 'Для импорта нужна связь с сервером.'
          : `Импорт не удался: ${String(error)}`,
      { title: 'Импорт', kind: 'error' });
    }
  }

  if (!loaded) return null;

  const categories = state.categories.filter((c) => !c.archived || c.id === categoryId);
  const elapsed = running ? formatElapsed(now - fromStamp(running.start).getTime()) : '00:00:00';

  if (view === 'settings') {
    return (
      <div className="app" ref={appRef}>
        <SettingsView settings={settings} lastSyncAt={state.lastSyncAt}
          onBack={settings.serverUrl ? () => setView('main') : undefined}
          onSave={async (next) => {
            await saveSettings(next);
            setAuthFailed(false);
            setSettings(next);
            setView('main');
          }} />
      </div>
    );
  }

  return (
    <div className="app" ref={appRef}>
      <div className="bar">
        <span className={running ? 'time running' : 'time'}>{elapsed}</span>
        {pending > 0 || needsToken
          ? <span className="dot" title={dotTitle} aria-label={dotTitle} />
          : <span className="ok-icon" title="Всё отправлено" aria-label="Всё отправлено">
              <CloudCheckIcon />
            </span>}
        <button className="icon-button ghost" aria-label="Меню" aria-expanded={view === 'menu'}
          onClick={() => setView(view === 'menu' ? 'main' : 'menu')}>
          <MenuIcon />
        </button>
      </div>

      <div className="body">
        {view === 'menu' && (
          <div className="menu" role="menu">
            <button role="menuitem" onClick={() => { setView('main'); void runSync(true); }}>
              <RefreshIcon /><span className="grow">Синхронизировать</span>
              {pending > 0 && <span className="count">{pending}</span>}
            </button>
            <button role="menuitem" onClick={() => void onImportLegacy()}>
              <ImportIcon />Импорт из старой версии
            </button>
            <button role="menuitem" disabled={!settings.serverUrl}
              onClick={() => { setView('main'); void openUrl(api.analyticsUrl); }}>
              <ChartIcon /><span className="grow">Открыть аналитику</span><ExternalIcon />
            </button>
            <button role="menuitem" onClick={() => setView('settings')}>
              <SettingsIcon /><span className="grow">Настройки</span>
              {needsToken && <span className="count">Проверь токен</span>}
            </button>
          </div>
        )}

        <input value={description} placeholder="Что делаешь?" maxLength={50}
          disabled={!!running} autoFocus
          onChange={(e) => setDescription(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') onStart(); }} />

        {newCategory === null
          ? (
            <div className="row">
              <select value={categoryId ?? ''} disabled={!!running}
                onChange={(e) => {
                  if (e.target.value === NEW_CATEGORY) setNewCategory('');
                  else setCategoryId(e.target.value ? Number(e.target.value) : null);
                }}>
                <option value="">Без категории</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                <option value={NEW_CATEGORY}>Новая категория…</option>
              </select>
              {running
                ? <button className="icon-button" title="Стоп" aria-label="Стоп" onClick={onStop}>
                    <StopIcon />
                  </button>
                : (
                  <>
                    <button className="icon-button" title="Старт" aria-label="Старт"
                      disabled={!canStart} onClick={onStart}><PlayIcon /></button>
                    <button className="icon-button" aria-label="Стоп без старта"
                      title="Записать, начав с конца прошлой задачи"
                      disabled={!canStart} onClick={onRecordWithoutStart}><StopIcon /></button>
                  </>
                )}
            </div>
          )
          : (
            <>
              <div className="row">
                <input value={newCategory} placeholder="Название категории" maxLength={50}
                  autoFocus onChange={(e) => { setNewCategory(e.target.value); setCategoryError(''); }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') void onCreateCategory();
                    if (e.key === 'Escape') { setNewCategory(null); setCategoryError(''); }
                  }} />
                <button onClick={() => void onCreateCategory()}>OK</button>
              </div>
              {categoryError && <p className="hint error">{categoryError}</p>}
            </>
          )}
      </div>
    </div>
  );
}

function SettingsView({ settings, lastSyncAt, onSave, onBack }: {
  settings: Settings;
  lastSyncAt: string | null;
  onSave: (settings: Settings) => Promise<void>;
  onBack?: () => void;
}) {
  const [serverUrl, setServerUrl] = useState(settings.serverUrl);
  const [token, setToken] = useState(settings.token);
  const [showToken, setShowToken] = useState(false);
  const [interval, setIntervalMinutes] = useState(settings.syncIntervalMinutes);
  const [check, setCheck] = useState<'idle' | 'ok' | 'fail' | 'auth' | 'checking'>('idle');
  const valid = /^https?:\/\/\S+$/.test(serverUrl.trim());

  // Reachability first (no token needed), then an authenticated call to check the token.
  async function onCheck() {
    if (!valid) return;
    setCheck('checking');
    const api = new TrackerApi(serverUrl, tauriFetch, token);
    if (!await api.ready().catch(() => false)) {
      setCheck('fail');
      return;
    }
    try {
      await api.activeTask();
      setCheck('ok');
    } catch (error) {
      setCheck(error instanceof AuthError ? 'auth' : 'fail');
    }
  }

  return (
    <>
      <div className="bar">
        {onBack
          ? <button className="icon-button ghost" title="Назад" aria-label="Назад" onClick={onBack}>
              <BackIcon />
            </button>
          : null}
        <span className="grow" />
        <button disabled={!valid} onClick={() => void onCheck()}>Проверить</button>
        <button disabled={!valid}
          onClick={() => void onSave({
            serverUrl: serverUrl.trim(), token: token.trim(), syncIntervalMinutes: interval,
          })}>
          Сохранить
        </button>
      </div>
      <div className="body">
        <p className="label">Адрес сервера</p>
        <input value={serverUrl} placeholder="http://192.168.0.38:8080" autoFocus
          onChange={(e) => { setServerUrl(e.target.value); setCheck('idle'); }} />
        {serverUrl && !valid && <p className="hint error">Адрес начинается с http:// или https://</p>}
        <p className="label">Токен</p>
        <div className="row">
          <input type={showToken ? 'text' : 'password'} value={token} autoComplete="off"
            spellCheck={false} placeholder="Выдаёт администратор сервера"
            onChange={(e) => { setToken(e.target.value); setCheck('idle'); }} />
          <button onClick={() => setShowToken(!showToken)}>
            {showToken ? 'Скрыть' : 'Показать'}
          </button>
        </div>
        {check === 'ok' && <p className="hint ok">Сервер отвечает</p>}
        {check === 'fail' && <p className="hint error">Сервер не отвечает</p>}
        {check === 'auth' && (
          <p className="hint error">{token.trim() ? 'Неверный токен' : 'Токен не указан'}</p>
        )}
        {check === 'checking' && <p className="hint">Проверяю…</p>}
        <p className="label">Повтор неотправленных записей</p>
        <select value={interval} onChange={(e) => setIntervalMinutes(Number(e.target.value))}>
          <option value={15}>Каждые 15 минут</option>
          <option value={60}>Каждый час</option>
          <option value={0}>Только вручную</option>
        </select>
        <p className="hint">
          Записи отправляются сразу. Если сервер недоступен, они ждут повтора.
          Последняя синхронизация: {lastSyncAt ?? 'ещё не было'}.
        </p>
      </div>
    </>
  );
}
