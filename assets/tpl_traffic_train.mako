{
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":train2: |     *Directions*    | :train2: "
			}
		},
        {
            "type": "divider"
        }
        %if not payload:
        ,{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No trains"
            }
        }
        %else:
        %for item in payload:
		,{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*${", ".join(item.products)}*: ${item.departure} - ${item.arrival} (+${item.delay_arrival})"
			}
		}
        %endfor
        %endif
	]
}