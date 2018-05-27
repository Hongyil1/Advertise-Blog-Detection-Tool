import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from mpi4py import MPI
import csv

def is_wordpress(url):

    web = "https://whatcms.org/"
    # delet the http:// or https://
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    # delet ending '/'
    if url.endswith('/'):
        url = url.strip('/')

    search_url = web + "?s=" + url + "&"

    # Use bfs
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    s = requests.Session()
    r = s.get(search_url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')
    s.close()
    # Get the pure text
    web_text = soup.get_text()
    # print(web_text)

    detect_text = "We haven't crawled"

    if detect_text in web_text:
        # print("No detected")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36')

        driver = webdriver.Chrome("./chromedriver", chrome_options=options)
        try:
            driver.get(search_url)
        except:
            driver.close()
            driver.quit()
            return False
        
        button = driver.find_element_by_class_name("btn-success")
        button.click()
        time.sleep(2)

        result = driver.find_elements_by_class_name("nowrap")
        elem_list = []

        for elem in result:
            elem_list.append(elem.text)

        driver.close()
        driver.quit()

        if "WordPress" in elem_list:
            return True
        else:
            return False

    else:
        if soup.find("div", {"class": "large text-center"}):
            target_div = soup.find("div", {"class": "large text-center"})
            result = target_div.a.get_text()
            # print("result: ", result)

            if "WordPress" == result:
                return True
            else:
                return False

        else:
            return False

# To detect whether a website can put advertisement
def has_advertise(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    s = requests.Session()
    try:
        r = s.get(url, headers=headers, timeout=15)
    except:
        s.close()
        return False

    soup = BeautifulSoup(r.text, 'lxml')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get the pure text
    web_text = soup.get_text()

    # Target words
    target_word = ["advertise", "media kit", "advertising", "promote with us", "advertise with us", "press kit",
                   "press room", "press inquiries", "advertising inquiries", "enquiries"]

    # break into lines and remove leading and trailing space on each, lowercase
    lines = [line.strip().lower() for line in web_text.splitlines() if 9 <= len(line.strip()) <= 21]

    if len(set(lines) & set(target_word)) > 0:
        return True
    else:
        return False

def write_target(target_list, rank, index):
    print("Rank{0} write to target file......".format(rank))
    with open("target/target_{0}.csv".format(index), 'a') as f:
        writer = csv.DictWriter(f, ['url'], extrasaction='ignore')
        for url in target_list:
            writer.writerow({'url': url})

def write_problem(problem_list, rank, index):
    print("Rank{0} write to problem file......".format(rank))
    with open("problem/problem_{0}.csv".format(index), 'a') as f1:
        writer = csv.DictWriter(f1, ['url'], extrasaction='ignore')
        for url in problem_list:
            writer.writerow({'url': url})

if __name__ == "__main__":

    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    if rank == 0:
        for index in range(14, 21):
            with open("target/target_{0}.csv".format(index), "w") as f:
                writer = csv.DictWriter(f, ['url'])
                writer.writeheader()

            with open("problem/problem_{0}.csv".format(index), "w") as f:
                writer = csv.DictWriter(f, ['url'])
                writer.writeheader()

            with open("time/time_{0}.txt".format(index), 'w') as f2:
                f2.write("")
    else:
        time.sleep(1)

    for index in range(14, 21):
        start_time = time.time()
        target_list = []
        problem_list = []
        with open("au_{0}.csv".format(index), "r") as f:
            for i, link in enumerate(f):
                if i > 0 and i % size == rank:
                    link = link.strip()
                    try:
                        # st1 = time.time()
                        ad = has_advertise(link)
                        # print("ad:", time.time() - st1)
                    except Exception as e:
                        # print("ad detection exception: ", link)
                        # print(e)
                        # problem_list.append(link)
                        # if len(problem_list) >= 20:
                        #     write_problem(problem_list, rank, index)
                        #     problem_list = []
                        continue
                    if ad:
                        try:
                            # st2 = time.time()
                            # print("url with ad: ", link)
                            wp = is_wordpress(link)
                            # print("wp: ", time.time() - st2)
                        except Exception as e:
                            print("wp detection exception: ", link)
                            print(e)
                            problem_list.append(link)
                            if len(problem_list) >= 5:
                                write_problem(problem_list, rank, index)
                                problem_list = []
                            continue
                        if wp:
                            print("target url: ", link[7:])
                            target_list.append(link)
                            if len(target_list) >= 10:
                                write_target(target_list, rank, index)
        if len(target_list) != 0:
            write_target(target_list, rank, index)
        if len(problem_list) != 0:
            write_problem(problem_list, rank, index)

        with open("time/time_{0}.txt".format(index), 'a') as f2:
            f2.write("Rank{0} finish: {1} \n".format(rank, round((time.time() - start_time), 2)))

        # print("rank{0} finishes au_{1}.csv file.........".format(rank, index))

