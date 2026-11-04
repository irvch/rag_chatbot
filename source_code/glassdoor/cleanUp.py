import json

def clean_reviews(reviews):
    # process ratings in review section
    if not reviews:
        return None
    ratings = reviews["ratings"]
    rating_distributions = reviews["ratingCountDistribution"]
    del rating_distributions["__typename"]
    for k, v in rating_distributions.items():
        del v["__typename"]


    

    overall_ratings = {
        "Business Outlook": ratings["businessOutlookRating"],
        "Career Opportunities": (ratings["careerOpportunitiesRating"], rating_distributions["careerOpportunities"]),
        "CEO": ratings["ceoRating"],
        "Compensation and Benefits": (ratings["compensationAndBenefitsRating"], rating_distributions["compensationAndBenefits"]),
        "Culture and Values": (ratings["cultureAndValuesRating"], rating_distributions["cultureAndValues"]),
        "Diversity and Inclusion": (ratings["diversityAndInclusionRating"], rating_distributions["diversityAndInclusion"]),
        "Overall": (ratings["overallRating"], rating_distributions["overall"]),
        "Senior Management": (ratings["seniorManagementRating"], rating_distributions["seniorManagement"]),
        "Work Life Balance": (ratings["workLifeBalanceRating"], rating_distributions["workLifeBalance"]),
        "Review Count": ratings["reviewCount"],
        "Recommend to Friend": rating_distributions["recommendToFriend"],
    }
    
    reviews_info = {
        "allReviewsCount": reviews["allReviewsCount"],
        "lastReviewDateTime": reviews["lastReviewDateTime"],
    }

    review_original = reviews["reviews"]
    reviews_new = []
    for review in review_original:
        # print(type(review))
        try:
            one_review = {
                "Cons": review["cons"],
                "Job Title": review["jobTitle"]["text"] if review["jobTitle"] else None,
                "Location": review["location"]["name"] if review["location"] else None,
                "Pros": review["pros"],
                "Business Outlook": review["ratingBusinessOutlook"],
                "Career Opportunities": review["ratingCareerOpportunities"],
                "CEO": review["ratingCeo"],
                "Compensation and Benefits": review["ratingCompensationAndBenefits"],
                "Culture and Values": review["ratingCultureAndValues"],
                "Diversity and Inclusion": review["ratingDiversityAndInclusion"],
                "Overall": review["ratingOverall"],
                "Recommend to Friend": review["ratingRecommendToFriend"],
                "Senior Leadership": review["ratingSeniorLeadership"],
                "Work Life Balance": review["ratingWorkLifeBalance"],
                "Review Date": review["reviewDateTime"],
                "Summary": review["summary"],
            }
            reviews_new.append(one_review)
        except TypeError:
            print(review["location"])
            raise
    return {
        "ratings": overall_ratings,
        "reviews": reviews_new,
        "reviews_info": reviews_info,
    }


def clean_one(data):
    new_data = {
        "rank": data["rank"],
        "company": data["company"],
        "industry": data["industry"],
        "city": data["city"],
        "state": data["state"],
        "zip": data["zip"],
        "website": data["website"],
        "employees": data["employees"],
        "revenue": data["revenue"],
        "valuation": data["valuation"],
        "profit": data["profit"],
        "ticker": data["ticker"],
        "ceo": data["ceo"],
    }
    rating_text = ""
    reviews_text = ""
    if "reviews" in data:
        new_data["reviews"] = clean_reviews(data["reviews"])

        lines = []
        lines.append(f"The Company has the following ratings: \n")
        lines.append(f"Average ratings for {new_data['company']}:\n")
        for key, value in new_data["reviews"]["ratings"].items():
            lines.append(f"{key}: ")
            if type(value) == tuple:
                lines.append(f"{value[0]}")
                lines.append("\nDistribution: \n\t")
                scores = sorted([f"{key[1]}: {val} " for key, val in value[1].items()])
                lines.append("\n\t".join(scores))
            else:
                if key == "Recommend to Friend":
                    lines.append("\n")
                    lines.append(f"\tRECOMMEND: {value['RECOMMEND']}\n")
                    lines.append(f"\tWONT RECOMMEND: {value['WONT_RECOMMEND']}\n")
                    
                else:
                    lines.append(f"{value}")
            lines.append("\n\n")
        rating_text = "".join(lines)


        lines = []
        lines.append(f"The company has {new_data['reviews']['reviews_info']['allReviewsCount']} reviews on Glassdoor. The last review was posted on {new_data['reviews']['reviews_info']['lastReviewDateTime']}. \n")
        lines.append(f"There are {len(new_data['reviews']['reviews'])} Reviews for {new_data['company']}:\n\n")
        for i in range(len(new_data["reviews"]["reviews"])):
            lines.append(f"Review {i+1}:\n")
            review = new_data["reviews"]["reviews"][i]
            order = ["Job Title", "Location", "Review Date", "Business Outlook", "Career Opportunities", "CEO", "Compensation and Benefits", "Culture and Values", "Diversity and Inclusion", "Overall", "Recommend to Friend", "Senior Leadership", "Work Life Balance"]
            for key in order:
                lines.append(f"\t{key}: {review[key]}\n")
            for key in ["Pros", "Cons", "Summary"]:
                value = review[key].replace('\n', '\n\t\t')
                lines.append(f"\n\t{key}: \n\t\t{value}\n\n")
            lines.append("\n")


        reviews_text = "".join(lines)
    # print(reviews_text)

    # write in english description of the company using info from new_data
    basic_text = f"""
{new_data['company']} is a {new_data['industry']} company based in {new_data["zip"]} {new_data['city']}, {new_data['state']}. 
The company has {new_data['employees']} employees and has a revenue of {new_data['revenue']} according to Fortune 500.
The company is valued at {new_data['valuation']} and has a profit of {new_data['profit']}. The CEO of the company is {new_data['ceo']}.

{rating_text}

{reviews_text}
---------------------------------------------------------------------------------------------------------------------

"""
    return new_data, basic_text
    
def clean_all(data):
    new_data = []
    text = []
    for company in data:
        json_data, clean_text = clean_one(company)
        new_data.append(json_data)
        with open(f"scrape/text/{json_data['ticker']}.txt", "w") as f:
            f.write(clean_text)
        # text.append(clean_text)
    
    # all_text = "".join(text)
    # with open("scrape/top500_reviews.txt", "w") as f:
    #     f.write(all_text)
    # with open("scrape/top500_reviews_clean.json", "w") as f:
    #     json.dump(new_data, f)

    return 
    


def main():
    with open("scrape/top500_reviews2.json") as f:
        data = json.load(f)

    clean_all(data)
    


if __name__ == "__main__":
    main()
