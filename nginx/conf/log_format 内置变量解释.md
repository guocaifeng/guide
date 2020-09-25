## nginx内置变量
```shell
$arg_name                      请求行中的参数名称，示例："http://www/baidu.com/?appid=123456",指的是"？"后面的"参数名=值"中的参数名部分。"？"问号是一个连接符，用于连接请求的URL中所携带的参数部分。
$args                          请求行中的参数部分。
$binary_remote_addr            以二进制的形式显示客户端地址，固定长度为4个字节。
$body_bytes_sent               传输给客户端的字节数，响应头不计算在内；这个变量和Apache的mod_log_config模块中的"%B"参数保持兼容
$bytes_sent                    传输给客户端的字节数
$connection                    连接的序列号。
$connection_requests           当前连接的请求数量。
$content_length                请求头部"Content-Length"信息部分，描述了HTTP消息主体内容的传输长度。
$content_type                  请求头部"Content_Type"信息部分，描述了HTTP消息主体内容类型。
$cookie_name                   Cookie的名字。
$document_root                 当前请求的由"location"中"root"指令或"alias"指令定义的资源位置，绝对路径或相对路径，这取决于你填的路径。
$document_uri                  当前请求的URI，等同于$uri。
$host                          请求头部的"Host"信息部分，如果请求中没有Host行，则等于设置的服务器名。
$hostname                      主机名。
$http_name                     任意请求头字段，"_"后面的"name"可以替换成任意的请求头部信息的字段,对于字段中的"-"需替换成"_"。比如"$http_host"。
$https                         如果开启了SSL，则此变量的值为"on"，否则为空。
$http_NAME               #匹配任意请求头字段；变量名中的后半部分NAME可以替换成任意请求头字段，如在配置文件中需要获取http请求头："Accept-Language"，$http_accept_language即可
$http_cookie
$http_host               #请求地址，即浏览器中你输入的地址（IP或域名）
$http_referer            #url跳转来源,用来记录从那个页面链接访问过来的
$http_user_agent         #用户终端浏览器等信息
$http_x_forwarded_for
$is_args                       如果请求中有参数，则此变量的值为"?"，否则为空。
$limit_rate                    用于设置限制响应速率，将设置的值写入到此变量中，方便被调用。
$msec                          当前Linux的时间，以毫秒为单位。
$nginx_version                 NGINX的版本。
$pid                           进程ID号。
$pipe                          如果请求是流水线作业，则此变量的值为"p"，否则为"."。
$proxy_protocol_addr           来自PROXY协议头的客户端地址，否则该变量的值为空。必须先通过在"listen"指令中设置参数"proxy_protocol"来启用PROXY协议。
$proxy_protocol_port           来自PROXY协议头的客户端端口，否则该变量的值为空。
必须先通过在"listen"指令中设置参数"proxy_protocol"来启用PROXY协议。
$query_string                  请求参数，等同于$args。
$realpath_root                 当前请求的由"location"中"root"指令或"alias"指令定义的资源位置，绝对路径。
$remote_addr                   请求的客户端地址。
$remote_port                   请求的客户端端口。
$remote_user                   基本身份验证模块提供的用户名，由客户端输入的用于身份验证的用户账号。
$request                       完整的原始的请求行。
$request_body                  请求主体。
此变量可在Location块中使用，变量的值在"proxy_pass、fastcgi_pass、uwsgi_pass、scgi_pass"指令处理时用于将请求转发给上游服务器（后端服务器）去处理。
$request_body_file             请求主体的临时文件的名称。
在处理结束后，需要删除该文件。要始终将请求写入到一个临时文件中，需要启用"client_body_in_file_only"。当在代理请求或对FastCGI / uwsgi / SCGI服务器的请求中传递临时文件的名称时，应分别通过proxy_pass_request_body off，fastcgi_pass_request_body off，uwsgi_pass_request_body off或scgi_pass_request_body off指令禁用传递请求体。
$request_completion            如果请求已完成，则该变量的值为"OK",否则为空。
$request_filename              当前连接请求的文件路径（URI），由"root"指令或"alias"指令定义的资源位置。
$request_id                    16个随机字节生成的唯一请求标识符，十六进制。
$request_length                请求长度，包括请求行，头部和请求主体。
$request_method                请求方法，通常是"GET"和"POST"。
$request_time                  请求处理时间，从客户端读取第一个字节后经过的时间，单位为毫秒。
$request_uri                   完整的原始的请求URI（带参数）。
$scheme                        请求的方式，"HTTP"或"HTTPS"。
$sent_http_name                任意响应头字段，"_name"可以指定任意响应头部字段，对于字段中的"-"需更换为"_"。比如"$sent_http_content_length"。
$sent_trailer_name             在响应结束时发送的任意字段，"_name"可以设置任意响应头部字段，对于字段中的"-"需更换为"_"。比如"$sent_trailer_hello_world hello world!"。
$server_addr                   接受请求的服务器的地址，计算此变量的值通常需要一次系统调用。为了避免系统调用，我们可以使用"listen"指令中指定地址。
$server_name                   接受请求的服务器的名称，一般指的是Server快中由"server_name"指令绑定的一个域名或一个虚拟主机名。
$server_port                   接受请求的服务器的端口。由"listen"指令中指定的端口。
$server_protocol               请求协议，通常是"HTTP/1.0、HTTP/1.1、HTTP/2.0"。
$status                        响应状态。
$tcpinfo_rtt,$tcpinfo_rttvar,$tcpinfo_snd_cwnd,$tcpinfo_rcv_space  有关客户端TCP连接的信息，在支持的TCP_INFO套接字选项的系统上可用。
$time_iso8601                  ISO 8601标准格式的当地时间。
$time_local                    通用日志格式的本地时间。
$uri                           当前请求的URI，等同于$document_uri。
```