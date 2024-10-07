default = """\
common:
  hosts: # 服务器监听地址
    - 0.0.0.0
  # - '::' # 取消这一行的注释，启用 ipv6 监听
  ports: # 服务器启动时所使用的端口
    - 9763
  ssl_info: # 服务器https配置
    # 这个服务器是否是https服务器，如果你使用了反向代理来转发这个服务器，如果它使用了https，也请将它设置为true
    is_https: false
    # python原生https监听
    enable: false
    ssl_ports:
      - 443
    path: # ssl证书的文件地址
      cert: /path/to/your/cer
      privkey: /path/to/your/private/key
  reverse_proxy: # 针对类似于nginx一类的反代的配置
    allow_public_ip: false # 允许来自公网的转发
    allow_proxy: true # 是否允许反代
    real_ip_header: X-Real-IP # 反代来源ip的来源头，不懂请保持默认
  debug_mode: false # 是否开启调试模式
  log_length_limit: 500 # 单条日志长度限制
  fakeip: 1.0.1.114 # 服务器在海外时的IP伪装值
  proxy: # 代理配置，HTTP与HTTPS协议需分开配置
    enable: false
    http_value: http://127.0.0.1:7890
    https_value: http://127.0.0.1:7890
  log_file: true # 是否存储日志文件
  cookiepool: false # 是否开启cookie池，这将允许用户配置多个cookie并在请求时随机使用一个，启用后请在module.cookiepool中配置cookie，在user处配置的cookie会被忽略，cookiepool中格式统一为列表嵌套user处的cookie的字典
  allow_download_script: true # 是否允许直接从服务端下载脚本，开启后可以直接访问 /script?key=你的请求key 下载脚本
  download_config: # 源脚本的相关配置
    name: 修改为你的源脚本名称
    intro: 修改为你的源脚本描述
    author: 修改为你的源脚本作者
    version: 修改为你的源版本
    filename: lx-music-source.js # 客户端保存脚本时的文件名（可能因浏览器不同出现不一样的情况）
    dev: true # 是否启用开发模式
    update: true # 是否开启脚本更新提醒
    # 可用参数
    # {updateUrl}为更新地址(带请求key)
    # {url}为请求时的url(不带请求的param)
    # {key}为请求时携带的key
    updateMsg: "源脚本有更新啦，更新地址:\\n{updateUrl}"
    quality:
      kw: [128k]
      kg: [128k]
      tx: [128k]
      wy: [128k]
      mg: [128k]
  local_music: # 服务器侧本地音乐相关配置，如果需要使用此功能请确保你的带宽足够
    audio_path: ./audio
    temp_path: ./temp

security:
  rate_limit: # 请求速率限制  填入的值为至少间隔多久才能进行一次请求，单位：秒，不限制请填为0
    global: 0 # 全局
    ip: 0 # 单个IP
  key:
    enable: false # 是否开启请求key，开启后只有请求头中包含key，且值一样时可以访问API
    ban: true
    values: # 填自己所有的请求key
      - "114514"
  whitelist_host: # 强制白名单HOST，不需要加端口号（即不受其他安全设置影响的HOST）
    - localhost
    - 0.0.0.0
    - 127.0.0.1
  check_lxm: false # 是否检查lxm请求头（正常的LX Music在内置源请求时都会携带这个请求头）
  lxm_ban: true # lxm请求头不存在或不匹配时是否将用户IP加入黑名单
  allowed_host: # HOST允许列表，启用后只允许列表内的HOST访问服务器，不需要加端口号
    enable: false
    blacklist: # 当用户访问的HOST并不在允许列表中时是否将请求IP加入黑名单，长度单位：秒
      enable: false
      length: 0
    list:
      - localhost
      - 0.0.0.0
      - 127.0.0.1
  banlist: # 是否启用黑名单（全局设置，关闭后已存储的值并不受影响，但不会再检查）
    enable: true
    expire: # 是否启用黑名单IP过期（关闭后其他地方的配置会失效）
      enable: true
      length: 604800

module:
  kg: # 酷狗音乐相关配置
    client: # 客户端请求配置，不懂请保持默认，修改请统一为字符串格式
      appid: "1005" # 酷狗音乐的appid，官方安卓为1005，官方PC为1001
      signatureKey: OIlwieks28dk2k092lksi2UIkp # 客户端signature采用的key值，需要与appid对应
      clientver: "12029" # 客户端versioncode，pidversionsecret可能随此值而变化
      pidversionsecret: 57ae12eb6890223e355ccfcb74edf70d # 获取URL时所用的key值计算验证值
      pid: "2" # url接口的pid
    tracker: # trackerapi请求配置，不懂请保持默认，修改请统一为字符串格式
      host: https://gateway.kugou.com
      path: /v5/url
      version: v5
      x-router: # 当host为gateway.kugou.com时需要追加此头，为tracker类地址时则不需要
        enable: true
        value: tracker.kugou.com
      extra_params: {} # 自定义添加的param，优先级大于默认，填写类型为普通的JSON数据，会自动转换为请求param
    user: # 此处内容请统一抓包获取（/v5/url），需要vip账号来获取会员歌曲，如果没有请留为空值，mid必填，可以瞎填一段数字
      token: ""
      userid: "0"
      mid: "114514"
      lite_sign_in: # 是否启用概念版自动签到，仅在appid=3116时运行
        enable: false
        interval: 86400
        mixsongmid: # mix_songmid的获取方式, 默认auto, 可以改成一个数字手动
          value: auto
      refresh_token: # 酷狗token保活相关配置，30天不刷新token会失效，enable是否启动，interval刷新间隔。默认appid=1005时有效，3116需要更换signatureKey
        enable: false
        interval: 86000
        login_url: http://login.user.kugou.com/v4/login_by_token

  tx: # QQ音乐相关配置
    vkeyserver: # 请求官方api时使用的guid，uin等信息，不需要与cookie中信息一致
      guid: "114514"
      uin: "10086"
    user: # 用户数据，可以通过浏览器获取，需要vip账号来获取会员歌曲，如果没有请留为空值，qqmusic_key可以从Cookie中/客户端的请求体中（comm.authst）获取
      qqmusic_key: ""
      uin: "" # key对应的QQ号
      refresh_login: # 刷新登录相关配置，enable是否启动，interval刷新间隔
        enable: false
        interval: 86000
    cdnaddr: http://ws.stream.qqmusic.qq.com/
    vkey_api: # 第三方Vkey获取API
      use_vkey_api: false
      vkey_api_url: "xxx"

  wy: # 网易云音乐相关配置
    user:
      cookie: "" # 账号cookie数据，可以通过浏览器获取，需要vip账号来获取会员歌曲，如果没有请留为空值
      refresh_login:
        enable: false
        interval: 86400

  mg: # 咪咕音乐相关配置
    user: # 研究不深，后两项自行抓包获取，网页端cookie
      by: ""
      session: ""
      useragent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36
      refresh_login: # cookie保活配置
        enable: false
        interval: 86400

  kw: # 酷我音乐相关配置，proto支持值：['bd-api', 'kuwodes']
    proto: bd-api
    user:
      uid: "0"
      token: ""
      device_id: "0"
    des: # kuwodes接口（mobi, nmobi）一类的加密相关配置
      f: kuwo
      need_encrypt: true # 是否开启kuwodes
      # {songId}为歌曲id
      # {map_quality}为map后的歌曲音质（酷我规范）
      # {raw_quality}为请求时的歌曲音质（LX规范）
      # {ext}为歌曲文件扩展名
      params: type=convert_url_with_sign&rid={songId}&quality={map_quality}&ext={ext}
      host: nmobi.kuwo.cn
      path: mobi.s
      # 这里是reponse_type的所有支持值，当设置为json时会使用到下面的两个值来获取url/bitrate，如果为text，则为传统的逐行解析方式
      response_type: json
      url_json_path: data.url
      bitrate_json_path: data.bitrate
      headers:
        User-Agent: okhttp/3.10.0

  gcsp: # 歌词适配后端配置
    # 请注意只允许私用，不要给原作者带来麻烦，谢谢
    enable: false # 是否启用歌词适配后端
    path: /client/cgi-bin/api.fcg # 后端接口地址
    enable_verify: false # 是否启用后端验证
    package_md5: "" # apk包的md5值，用于验证
    salt_1: "NDRjZGIzNzliNzEe" # 后端验证参数1
    salt_2: "6562653262383463363633646364306534333668" # 后端验证参数2

  cookiepool:
    kg:
      - userid: "0"
        token: ""
        mid: "114514"
        lite_sign_in: # 是否启用概念版自动签到，仅在appid=3116时运行
          enable: false
          interval: 86400
          mixsongmid: # mix_songmid的获取方式, 默认auto, 可以改成一个数字手动
            value: auto
        refresh_login: # cookie池中对于此账号刷新登录的配置，账号间互不干扰
          enable: false
          login_url: http://login.user.kugou.com/v4/login_by_token

    tx:
      - qqmusic_key: ""
        uin: ""
        refresh_login: # cookie池中对于此账号刷新登录的配置，账号间互不干扰
          enable: false
          interval: 86000

    wy:
      - cookie: ""
        refresh_login: # cookie池中对于此账号刷新登录的配置，账号间互不干扰
          enable: false
          interval: 86400

    mg:
      - by: ""
        session: ""
        useragent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36
        refresh_login:
          enable: false
          interval: 86400

    kw:
      - uid: "0"
        token: ""
        device_id: "0"
"""
