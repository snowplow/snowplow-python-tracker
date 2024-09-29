from snowplow_tracker import (
    Tracker,
    Emitter,
    Subject,
    SelfDescribingJson,
    PageView,
    SelfDescribing,
)
import snowflake.connector
import brotli
import gzip


TRACKER_COLS = [
"PLATFORM",
"EVENT",
"USER_ID",
"USER_IPADDRESS",
"DOMAIN_USERID",
"DOMAIN_SESSIONIDX",
"NETWORK_USERID",
"PAGE_URL",
"PAGE_TITLE",
"PAGE_REFERRER",
"BR_LANG",
"BR_COOKIES",
"BR_COLORDEPTH",
"BR_VIEWWIDTH",
"BR_VIEWHEIGHT",
"OS_TIMEZONE",
"DVCE_SCREENWIDTH",
"DVCE_SCREENHEIGHT",
"DOC_CHARSET",
"DOC_WIDTH",
"DOC_HEIGHT",
"DVCE_SENT_TSTAMP",
"DOMAIN_SESSIONID",
"TRUE_TSTAMP",
"CONTEXTS_COM_SNOWPLOWANALYTICS_SNOWPLOW_WEB_PAGE_1",
"CONTEXTS_SNOWPLOWANALYTICS_COM_USER_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_IMPRESSION_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_CLICK_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_ACTIVATION_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_VIEW_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_DISMISS_1",
"UNSTRUCT_EVENT_SNOWPLOWANALYTICS_COM_PRODUCT_CLICK_1",
"CONTEXTS_SNOWPLOWANALYTICS_COM_PRODUCT_1",
"CONTEXTS_SNOWPLOWANALYTICS_COM_CART_1",
"CONTEXTS_SNOWPLOWANALYTICS_COM_CHECKOUT_STEP_1",
"CONTEXTS_SNOWPLOWANALYTICS_COM_TRANSACTION_1",
"event_name"
]

ctx = snowflake.connector.connect(
    user="XXXXXXXXXXXX",
    password="XXXXXXXXXXXX",
    account="XXXXXXXXXXXX"
)

def gzip_compression(data): 
    return gzip.compress(bytes(data, "UTF-8"))   

def brotli_compression(data):
    return brotli.compress(bytes(data, "UTF-8"))     


def get_snowflake_data(num_rows):
    cols = ",".join(str(element) for element in TRACKER_COLS)
    sql_comm = "select "
    sql_comm += cols
    sql_comm += " from ANALYTICS_DEV_DB.ATOMIC.EVENTS limit " + str(num_rows)

    cs = ctx.cursor()
    try:
        df = cs.execute(sql_comm)
        ret = df.fetchall()
    finally:
        cs.close()
    ctx.close()
    return ret

def create_event(row, tracker):
    subject= Subject().set_user_id(row[2]).set_ip_address(row[3]).set_domain_user_id(row[4]).set_domain_session_index(row[5]).set_network_user_id(row[6]).set_lang(row[10]).set_platform(row[0]).set_screen_resolution(row[13], row[14]).set_domain_session_id(row[22])

    contexts = []
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_COM_SNOWPLOWANALYTICS_SNOWPLOW_WEB_PAGE_1/jsonschema/1-0-0",
                row[24]
            ))
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_SNOWPLOWANALYTICS_COM_USER_1/jsonschema/1-0-0",
                row[25]
            ))
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_SNOWPLOWANALYTICS_COM_PRODUCT_1/jsonschema/1-0-0",
                row[32]
            ))
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_SNOWPLOWANALYTICS_COM_CART_1/jsonschema/1-0-0",
                row[33]
            ))
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_SNOWPLOWANALYTICS_COM_CHECKOUT_STEP_1/jsonschema/1-0-0",
                row[34]
            ))
    contexts.append( SelfDescribingJson(
                "iglu:com.my_company/CONTEXTS_SNOWPLOWANALYTICS_COM_TRANSACTION_1/jsonschema/1-0-0",
                row[35]
            ))

    if(row[1] == 'page_view'):
        event = PageView(row[7], row[8], row[9], subject, context=contexts)
    else:
        event_name = row[36] 
        event_types = {"impression": row[26], "product_click": row[31], 'transaction': row[35]}
        if event_name in event_types.keys():
            event_desc = event_types[event_name]
        else: 
            event_desc="unstruct"
        
        event = SelfDescribing(SelfDescribingJson("iglu:com.snowplowanalytics.snowplow/unstruct_event/1-0-0", event_desc), event_subject=subject, context=contexts)

    tracker.track(event)

def run_test(data_length, tracker):
    df = get_snowflake_data(data_length)
    for row in df:
        create_event(row, tracker)
    tracker.flush()

def main():
    data_length = 10 # Edit for different length tests
    e = Emitter("localhost", batch_size=data_length, buffer_capacity=10000000, request_timeout=1)
    tracker = Tracker(namespace="snowplow_tracker", emitters=e, encode_base64=False)
    run_test(data_length, tracker=tracker)
    
if __name__ == "__main__":
    main()
