import asyncio
import nodriver as uc
import time
import os
from fastapi import FastAPI
from typing import Dict
from datetime import datetime
import base64
import requests
import shutil
from starlette.config import Config
from starlette.datastructures import Secret
import random


config = Config("../.env")

app = FastAPI(
    title="Bot",
    version="0.0.2"
)

PROXY = config("PROXY")
USERNAME = config("USERNAME")
PASSWORD = config('PASSWORD')



# PROXY = "gw.dataimpulse.com:823"
# USERNAME = "cc72c1209265887c7f62"
# PASSWORD = "5a62f7c1961e3096"


main_tab: uc.Tab



async def auth_challenge_handler(event: uc.cdp.fetch.AuthRequired):
    global main_tab
    # Split the credentials
    # Respond to the authentication challenge
    asyncio.create_task(
        main_tab.send(
            uc.cdp.fetch.continue_with_auth(
                request_id=event.request_id,
                auth_challenge_response=uc.cdp.fetch.AuthChallengeResponse(
                    response="ProvideCredentials",
                    username=USERNAME,
                    password=PASSWORD,
                ),
            )
        )
    )




async def req_paused(event: uc.cdp.fetch.RequestPaused):
    global main_tab
    asyncio.create_task(
        main_tab.send(
            uc.cdp.fetch.continue_request(request_id=event.request_id)
        )
    )




async def generator():
    browser = await uc.start(
        browser_args=[f"--proxy-server={PROXY}"],
    )
    main_tab = await browser.get("draft:,")
    main_tab.add_handler(uc.cdp.fetch.RequestPaused, req_paused)
    main_tab.add_handler(
        uc.cdp.fetch.AuthRequired, auth_challenge_handler
    )
    await main_tab.send(uc.cdp.fetch.enable(handle_auth_requests=True))
    # return await asyncio.gather(*browser, return_exceptions=True)

    return browser




async def main(data):
    global main_tab

    transaction_successfull: bool = False
    transaction_date_ = ""
    transaction_id_ = ""
    response_ = []
    voucher_dict = {
        "status": "completed",
        "voucher_code": "ABC123",
        "used_time": "2023-04-24 12:00:00",
        "screenshot": "http://example.com/screenshot.jpg"
    }


    response_dict = {
        "order_id": data['order_id'],
        "order_status": "done",
        "vouchers": [],
        "invalid_ids": []
        
    }

    response_endpoint: str = "https://gameheaven.net/wp-json/custom-order-plugin/v1/orders"

    


    with open(os.path.join(os.getcwd(),"trxids.txt"), 'r') as file:
        trx_ids = file.readlines()
        trx_ids = [ids.strip() for ids in trx_ids]

    # print(trx_ids)


    if data['trxid'] in trx_ids:

        # print("Duplicate order!!!")

        response_dict["order_status"] = "duplicate order"

        return response_dict
        

    # with open(os.path.join(os.getcwd(),"trxids.txt"), "a") as f:
    #     f.write(data['trxid']+"\n")

    while True:

        try:
            browser = await uc.start(
                browser_args=[f"--proxy-server={PROXY}"],
            )
            main_tab = await browser.get("draft:,")
            main_tab.add_handler(uc.cdp.fetch.RequestPaused, req_paused)
            main_tab.add_handler(
                uc.cdp.fetch.AuthRequired, auth_challenge_handler
            )
            await main_tab.send(uc.cdp.fetch.enable(handle_auth_requests=True))

            break
            

        except Exception as e:
            print("Exception caught")




    # page = await browser.get('https://whatismyipaddress.com/')
    # input("wait")


    try:
        page = await browser.get('https://shop.garena.my/app/100067/idlogin')
        await page.sleep(random.uniform(2, 5))
        
        for order_item in data['order_items']:

            
            
            # content = await page.find("player id login", timeout=20)

            # if content:
            #     print("Hai na re baba")

            try:
                player_id_input = await page.select("input[name=playerId]", timeout=40)

                if player_id_input:
                    await player_id_input.clear_input()
                    await player_id_input.click()
                    await player_id_input.send_keys(str(order_item['player_id']))
                    await page.sleep(random.uniform(2, 5))
                    # time.sleep(2)
                
            except Exception as e:
                print("Player input not found\n\nTry again later !!!\n\n")

                response_dict['order_status'] = 'failed'
                response_dict['details'] = "Input field not found. Try again later"

                return response_dict


            login_btn = await page.select("input[value=Login]")

            if login_btn:
                await login_btn.click()
                # await page.sleep(1)
                # time.sleep(2)


            try:

                server_mismatch_check = await page.find("Proceed to correct shop", timeout=2)

                if server_mismatch_check:
                    # print("Server mismatch")
                    
                    response_dict['invalid_ids'].append(str(order_item['player_id']))
                    continue

            except Exception as e:
                pass



            try:
                login_status = await page.find("Invalid Player ID", timeout=2)

                if login_status:
                    print("Invalid account")

                    response_dict['invalid_ids'].append(str(order_item['player_id']))

                    continue

            except Exception as e:
                print("Logged In")




            # input("wait")

            logged_In_main_page = "https://shop.garena.my/app/100067/buy/0"


            for item in order_item['items']:

                print(item)

                for i in range(len(item['voucher_data'])):

                    
                    for j in range(item['voucher_data'][i]['voucher_quantity']):

                        # print(i, j)

                        proceed_to_payment_btn = await page.find('Proceed to Payment')

                        if proceed_to_payment_btn:
                            await proceed_to_payment_btn.click()
                            await page.sleep(random.uniform(6, 8))
                            # time.sleep(10)



                        try:



                            if "2530" in item['voucher_data'][i]['voucher_value']:
                                print("2530 found!!")

                                diamonds_div2 = await page.find("2530 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")


                            elif "25" in item['voucher_data'][i]['voucher_value']:
                                print("25 found!!")

                                diamonds_div = await page.find("25 diamond")

                                if diamonds_div:
                                    await diamonds_div.click()
                                    time.sleep(1)

                                
                                else:
                                    print("Diamond with required quantity not found!!")


                            elif "50" in item['voucher_data'][i]['voucher_value']:
                                print("50 found!!")

                                diamonds_div2 = await page.find("50 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")

                            
                            
                            elif "115" in item['voucher_data'][i]['voucher_value']:
                                print("115 found!!")

                                diamonds_div2 = await page.find("115 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")


                            elif "1240" in item['voucher_data'][i]['voucher_value']:
                                print("1240 found!!")

                                diamonds_div2 = await page.find("1240 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")



                            elif "240" in item['voucher_data'][i]['voucher_value']:
                                print("240 found!!")

                                diamonds_div2 = await page.find("240 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")




                            elif "610" in item['voucher_data'][i]['voucher_value']:
                                print("610 found!!")

                                diamonds_div2 = await page.find("610 diamond")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")




                            elif "weekly" in item['voucher_data'][i]['voucher_value'].lower():

                                print("weekly found!!")


                                diamonds_div2 = await page.find("Weekly Membership")
                                # await diamonds_div2.highlight_overlay()


                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    # print("weekly clicked !!!")

                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")





                            elif "monthly" in item['voucher_data'][i]['voucher_value'].lower():

                                print("monthly found!!")

                                diamonds_div2 = await page.find("Monthly Membership")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")



                            elif "level up pass" in item['voucher_data'][i]['voucher_value'].lower():

                                print("level up pass found!!")

                                diamonds_div2 = await page.find("Level Up Pass")

                                if diamonds_div2:
                                    await diamonds_div2.click()
                                    time.sleep(1)
                                
                                else:
                                    print("Diamond with required quantity not found!!")


                        except IndexError as e:
                            print(e)
                            print(i, j)
                            exit(0)


                        except Exception as e:
                            print("Failed to find required diamonds div")

                            filename = await page.save_screenshot()

                            with open(filename, "rb") as file:
                                image_data = file.read()

                            # Encode the image data as Base64
                            image_base64 = base64.b64encode(image_data).decode()

                            voucher_dict = {
                                "status": "failed",
                                "voucher_code": item['voucher_data'][i]['voucher_codes'][j],
                                "used_time": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                                "transaction_id": "",
                                "screenshot": image_base64
                            }

                            response_dict["vouchers"].append(voucher_dict)

                            shutil.move(filename, "outputImages/")
                            
                            continue


                        try:
                            await page.sleep(random.uniform(2, 5))
                            payment_channel_selection = await page.find("Physical Vouchers")

                            if payment_channel_selection:
                                await payment_channel_selection.click()
                                await page.sleep(2)


                        except Exception as e:
                            print("Payment selection channel not found")


                        voucher = item['voucher_data'][i]['voucher_codes'][j]


                        if "UPBD" in voucher:

                            try:
                                voucher_platform = await page.find("UP Gift Card")

                                if voucher_platform:
                                    await voucher_platform.click()
                                    time.sleep(1)

                            
                            except Exception as e:
                                print("Voucher platform not found!!!")


                        elif "BDMB" in voucher:

                            try:
                                voucher_platform2 = await page.find("UniPin Voucher")

                                if voucher_platform2:
                                    await voucher_platform2.click()
                                    time.sleep(1)

                            
                            except Exception as e:
                                print("Voucher platform not found!!!")
                        


                        pin__ = item['voucher_data'][i]['voucher_codes'][j].split(" ")[1]

                        pin_ = pin__.split("-")
                        
                        item['voucher_data'][i]['voucher_codes'][j] = item['voucher_data'][i]['voucher_codes'][j].replace("-", "").replace("BDMB", "").replace("UPBD", "")

                        serial_ = item['voucher_data'][i]['voucher_codes'][j].split(" ")[0]



                        try:
                            await page.sleep(random.uniform(2, 5))
                            serial_input = await page.find("input[name=serial_1]")

                            if serial_input:
                                await serial_input.send_keys(serial_[0])
                                time.sleep(1)

                            serial_input2 = await page.find("input[name=serial_2]")
                            if serial_input2:
                                await serial_input2.send_keys(serial_[2:])

                        except:
                            print("serial number entry not found")



                        try:

                            for k in range(len(pin_)):
                                pin_input = await page.find(f"input[name=pin_{k+1}]")

                                if pin_input:
                                    await pin_input.send_keys(pin_[k])

                            time.sleep(3)

                        except Exception as e:
                            print("Failed to access pin input field!!!")



                        try:
                            confirm_btn = await page.find("confirm")

                            if confirm_btn:
                                await confirm_btn.click()
                                time.sleep(1)
                            
                        except Exception as e:
                            pass




                        try:
                            submission_status = await page.find("Transaction successful", timeout=3)

                            if submission_status:

                                transaction_id = await page.find("div[id=trans_id]")
                                
                                if transaction_id:
                                    transaction_id_ = transaction_id.text.strip()
                                    # print(transaction_id_)
                                

                                try:
                                    transaction_date = await page.find("body > div.full100-flex-col > div.container.pt-5 > div > div.litepage-fullheight.px-sm-checkout > div.checkout-details-container > div:nth-child(2) > div.details-value")

                                    if transaction_date:
                                        transaction_date_ = transaction_date.text.strip()
                                        # print(transaction_date_)


                                except Exception as e:
                                    pass



                                try:
                                    back_to_merchant_btn = await page.find("Back to merchant")

                                    if back_to_merchant_btn:
                                        await back_to_merchant_btn.click()
                                        time.sleep(2)
                                        # await page.save_screenshot()

                                except Exception as e:
                                    print("Failed to find back to merchant button")


                                with open(os.path.join(os.getcwd(),"trxids.txt"), "a") as f:
                                    f.write(data['trxid']+"\n")

                                transaction_successfull = True

                                filename = await page.save_screenshot()

                                with open(filename, "rb") as file:
                                    image_data = file.read()

                                # Encode the image data as Base64
                                image_base64 = base64.b64encode(image_data).decode()


                                voucher_dict = {
                                    "status": "completed",
                                    "voucher_code": voucher,
                                    "used_time": transaction_date_,
                                    "transaction_id": transaction_id_,
                                    "screenshot": image_base64
                                }

                                response_dict["vouchers"].append(voucher_dict)

                                shutil.move(filename, "outputImages/")

                        except Exception as e:
                            print("Transation failed !!!")




                        if not transaction_successfull:

                            try:
                                submission_result = await page.find("Please use supported vouchers.", timeout=2)

                                if submission_result:
                                    print("Top up using voucher failed!!!")
                                    transaction_successfull = True


                                    filename = await page.save_screenshot()

                                    with open(filename, "rb") as file:
                                        image_data = file.read()

                                    # Encode the image data as Base64
                                    image_base64 = base64.b64encode(image_data).decode()


                                    voucher_dict = {
                                        "status": "failed",
                                        "voucher_code": voucher,
                                        "used_time": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                                        "transaction_id": "",
                                        "screenshot": image_base64
                                    }

                                    response_dict["vouchers"].append(voucher_dict)

                                    shutil.move(filename, "outputImages/")

                            except Exception as e:
                                pass



                        if not transaction_successfull:

                            try:
                                submission_statuss = await page.find("UNAUTHORIZED", timeout=3)

                                if submission_statuss:
                                    print("Transaction successfull !!!!")
                                    transaction_successfull = True

                                    filename = await page.save_screenshot()

                                    with open(filename, "rb") as file:
                                        image_data = file.read()

                                    # Encode the image data as Base64
                                    image_base64 = base64.b64encode(image_data).decode()


                                    voucher_dict = {
                                        "status": "completed",
                                        "voucher_code": voucher,
                                        "used_time": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                                        "transaction_id": "",
                                        "screenshot": image_base64
                                    }

                                    response_dict["vouchers"].append(voucher_dict)

                                    shutil.move(filename, "outputImages/")



                            except Exception as e:
                                pass



                        if not transaction_successfull:

                            try:
                                submission_stat = await page.find("Consumed Voucher", timeout=3)

                                if submission_stat:
                                    print("Voucher already consumed !!!!")


                                    filename = await page.save_screenshot()

                                    with open(filename, "rb") as file:
                                        image_data = file.read()

                                    # Encode the image data as Base64
                                    image_base64 = base64.b64encode(image_data).decode()


                                    voucher_dict = {
                                        "status": "failed",
                                        "voucher_code": voucher,
                                        "used_time": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                                        "transaction_id": "",
                                        "screenshot": image_base64
                                    }

                                    response_dict["vouchers"].append(voucher_dict)

                                    shutil.move(filename, "outputImages/")



                            except Exception as e:
                                pass




                        # input("wait")
                        page = await page.get(logged_In_main_page)
                        transaction_successfull = False

                        time.sleep(2)

                # await page.sleep(1)

            #log out of current account.
            page = await browser.get('https://shop.garena.my/app/100067/idlogin', new_tab=True)
            await page.bring_to_front()
            




        # await page.close()


        endpoint_response = requests.post(response_endpoint, json={
            "result": response_dict
        })

        # print(endpoint_response.text)

        return response_dict
    

    finally:
        browser.stop()




@app.post("/order/")
async def run(payload: Dict):

    result = await main(payload)

    return {"result": result}




@app.get("/test/")
async def hello():
    return [
        {
        "status": "completed",
        "order_id": "74",
        "voucher_code": "ABC123",
        "used_time": "2023-04-24 12:00:00",
        "screenshot": "http://example.com/screenshot.jpg"
        },
        {
        "status": "failed",
        "order_id": "74",
        "voucher_code": "ABC1234",
        "used_time": "2023-04-24 12:02:00",
        "screenshot": "http://example.com/screenshot2.jpg"
        },
        {
        "status": "completed",
        "order_id": "74",
        "voucher_code": "ABC1235",
        "used_time": "2023-04-24 12:09:00",
        "screenshot": "http://example.com/screenshot3.jpg"
        }     
    ]




if __name__ == '__main__':


    #8287664703
    #6954381607

    # payload = {
    # "order_id": "001",
    # "player_id": 8287664703,
    # "items": [
    #     {
    #         "amount": "25dm",
    #         "quantity": 1,
    #         "voucher": "UPBD-G-S-00047903 5229-1272-1132-2523"
    #     },
    #     {
    #         "amount": "50dm",
    #         "quantity": 2,
    #         "voucher": ["BDMB-K-S-00619551 8661-2622-4656-4232", "BDMB-K-S-00619682 3523-3942-5937-2952"]
    #     }
    # ],
    # "status": "processing",
    # "trxid": "BDO4SVBT1O"
    # }



    payload = {
  "domain": "https://gameheaven.net",
  "order_id": "56025",
  "order_items": [
    {
      "player_id": "3840381346",
      "items": [
        {
          "product_id": 498,
          "variation_id": 550,
          "variation_name": "💎 355 Diamonds",
          "amount": "225BDT",
          "quantity": 1,
          "voucher_data": [
            {
              "voucher_value": "25",
              "voucher_quantity": 1,
              "voucher_codes": [
                "UPBD-Q-S-00188996 5296-7643-3163-3955"
              ]
            },
          ]
        }
      ],
      "parent_product_id": 498,
      "topup_url": "https://shop.garena.my/app/100067/idlogin"
    },
    {
      "player_id": "1706983935",
      "items": [
        {
          "product_id": 498,
          "variation_id": 549,
          "variation_name": "💎 505 Diamonds",
          "amount": "320BDT",
          "quantity": 1,
          "voucher_data": [
            {
              "voucher_value": "25 Diamond",
              "voucher_quantity": 2,
              "voucher_codes": [
                "BDMB-L-S-00242685 1526-4656-5576-2155",
                "BDMB-S-S-00170201 2756-3496-1366-7633"
              ]
            },
            {
              "voucher_value": "25 Diamond",
              "voucher_quantity": 1,
              "voucher_codes": [
                "BDMB-K-S-00581691 1596-4497-1912-4295"
              ]
            }
          ]
        }
      ],
      "parent_product_id": 498,
      "topup_url": "https://shop.garena.my/app/100067/idlogin"
    }
  ],
  "status": "processing",
  "trxid": "test2"
}

    # since asyncio.run never worked (for me)
    # uc.loop().run_until_complete(main(payload))